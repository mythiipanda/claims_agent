from google.cloud import bigquery
import pandas as pd
import numpy as np
import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ID = os.environ.get('PROJECT_ID', 'qwiklabs-gcp-01-939f4fda1e9a')
DATASET_ID = os.environ.get('DATASET_ID', 'humana_hackathon')

logger.info(f"Initializing BigQuery client for project: {PROJECT_ID}, dataset: {DATASET_ID}")
client = bigquery.Client(project=PROJECT_ID)

def _serialize_df(df: pd.DataFrame):
    """Helper to convert date/datetime columns to string and handle NaNs."""
    if df.empty:
        return []
        
    # Convert all columns to strings if they are date/datetime types
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x.isoformat() if isinstance(x, (datetime.date, datetime.datetime)) else x)
                
    # Handle NaNs and convert to dict
    return df.replace({np.nan: None}).to_dict(orient='records')

def query_claims(claim_id: str = None, member_id: str = None):
    """Queries BigQuery for a specific claim or member."""
    logger.info(f"Querying claims with claim_id={claim_id}, member_id={member_id}")
    if claim_id:
        query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.claims` WHERE claim_id = @claim_id"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("claim_id", "STRING", claim_id)]
        )
    elif member_id:
        query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.claims` WHERE member_id = @member_id"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("member_id", "STRING", member_id)]
        )
    else:
        return "Please provide a claim_id or member_id."
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.to_dataframe()
        
        if results.empty:
            logger.warning("No claim records found.")
            return "No claim found."
            
        return _serialize_df(results)
    except Exception as e:
        logger.error(f"Error querying claims: {e}")
        return f"Error querying claims: {str(e)}"

def query_benefits(cpt_code: str):
    """Queries BigQuery for benefits and PA requirements by CPT code."""
    logger.info(f"Querying benefits for CPT code: {cpt_code}")
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.coverage_rules` WHERE cpt_code = @cpt_code"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("cpt_code", "STRING", cpt_code)]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.to_dataframe()
        
        if results.empty:
            logger.warning(f"No coverage rules found for CPT {cpt_code}")
            return f"No coverage rules found for CPT {cpt_code}."
        
        return _serialize_df(results)
    except Exception as e:
        logger.error(f"Error querying benefits: {e}")
        return f"Error querying benefits: {str(e)}"

def verify_roi(member_id: str, caller_name: str):
    """Checks BigQuery if a caller has a valid ROI on file for a member."""
    logger.info(f"Verifying ROI for member_id={member_id}, caller_name={caller_name}")
    query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.roi_authorizations` 
        WHERE member_id = @member_id 
        AND LOWER(authorized_caller_name) LIKE LOWER(@caller_name)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("member_id", "STRING", member_id),
            bigquery.ScalarQueryParameter("caller_name", "STRING", f"%{caller_name}%")
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.to_dataframe()
        
        if results.empty:
            logger.warning(f"No ROI found for {caller_name} on member {member_id}")
            return {"authorized": False, "reason": "No ROI on file for this caller."}
        
        record_dict = _serialize_df(results)[0]
        
        if record_dict['auth_expired'] == True:
            return {"authorized": False, "reason": "ROI has expired."}
        if not record_dict['auth_on_file']:
             return {"authorized": False, "reason": "ROI record exists but authorization is not on file."}
        
        logger.info("ROI verification successful.")
        return {"authorized": True, "record": record_dict}
    except Exception as e:
        logger.error(f"Error verifying ROI: {e}")
        return {"authorized": False, "reason": f"System error during ROI verification: {str(e)}"}

def scan_risks():
    """Scans BigQuery for high-risk claims and compliance flags."""
    logger.info("Scanning for operational and compliance risks.")
    risk_claims_query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.claims` WHERE denial_risk_flag = TRUE LIMIT 5"
    compliance_query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.compliance_flags` WHERE severity = 'High' AND resolved = FALSE"
    
    try:
        risk_claims = client.query(risk_claims_query).to_dataframe()
        compliance_risks = client.query(compliance_query).to_dataframe()
                
        logger.info(f"Found {len(risk_claims)} risk claims and {len(compliance_risks)} high risk compliance flags.")
        return {
            "risk_claims_count": len(risk_claims),
            "high_risk_compliance_count": len(compliance_risks),
            "samples": _serialize_df(risk_claims),
            "compliance_samples": _serialize_df(compliance_risks)
        }
    except Exception as e:
        logger.error(f"Error scanning risks: {e}")
        return {"error": str(e)}
