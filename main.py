from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from agents.factory import orchestrator
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
session_service = InMemorySessionService()

@app.get("/")
async def get_index():
    return FileResponse("templates/index.html")

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted.")
    
    # Initialize GADK runner for this session
    runner = Runner(app_name="HumanaClaimStoryApp", agent=orchestrator, session_service=session_service)
    
    # Create the session
    await session_service.create_session(session_id="web_session", user_id="web_user", app_name="HumanaClaimStoryApp")

    try:
        while True:
            # Receive message from frontend
            data = await websocket.receive_text()
            msg = json.loads(data)
            user_input = msg.get("input", "")
            
            if not user_input:
                continue

            logger.info(f"User input: {user_input}")
            
            # Use GADK runner to process the message
            # The agent will now stream responses back via the runner
            async for event in runner.run_async(user_id="web_user", session_id="web_session", new_message=Content(role="user", parts=[Part.from_text(text=user_input)])):
                # Log event to inspect structure
                logger.info(f"Event type: {type(event)}, Event: {event}")
                
                # Extract text if event has a text attribute
                response_text = ""
                if hasattr(event, 'text') and event.text:
                    response_text = event.text
                elif hasattr(event, 'content') and event.content:
                    # If content is a Content object, try to extract text from its parts
                    if hasattr(event.content, 'parts'):
                        response_text = " ".join([p.text for p in event.content.parts if p.text])
                    else:
                        response_text = str(event.content)
                
                if response_text:
                    logger.info(f"Agent response: {response_text}")
                    await websocket.send_json({"response": response_text})
                    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed.")
