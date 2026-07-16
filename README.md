# Claim Story AI: Proactive Member & Claims Intelligence System

## Mission
To shift healthcare call centers from reactive explanation to proactive prevention and self-service transparency using a multi-agent system.

## Key Use Cases
- **Claim Story Timeline:** Generates a plain-language explanation of claim status, denials, and required actions.
- **Benefits & Coverage Lookup:** Instant responses for CPT codes, cost-sharing, and Prior Authorization (PA) requirements.
- **ROI Gap Screening:** Detects unauthorized callers and proactively routes them to ROI forms before they reach an agent.
- **Operational Risk Monitoring:** Surfaces system health signals and compliance gaps (e.g., stalled claims).

## Architecture
- **Orchestrator:** Central hub for request routing and proactive intelligence.
- **ClaimStoryAgent:** Specialized in claim history and plain-language denial explanation.
- **BenefitsAgent:** Expert in coverage rules and PA requirements.
- **ROIAgent:** Privacy guardian that screens for authorization gaps.
- **RiskMonitorAgent:** Background monitor for compliance and system health.

## Data Sources
- **BigQuery:** Production-ready data layer in the `humana_hackathon` dataset.
- **Unstructured Data:** Call transcripts used for scenario modeling and scenario validation.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the system: `python main.py`
