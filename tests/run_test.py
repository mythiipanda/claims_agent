import asyncio
from agents.factory import orchestrator
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

async def run_scenario():
    print("Starting call center scenario test...")
    
    session_service = InMemorySessionService()
    runner = Runner(app_name="TestApp", agent=orchestrator, session_service=session_service)
    
    # Create the session explicitly
    await session_service.create_session(session_id="test_session", user_id="test_user", app_name="TestApp")
    
    # Define a scenario
    scenario = [
        "What is the status of my claim with claim_id C12345?",
        "What about benefits for CPT code 99213?",
    ]
    
    for user_input in scenario:
        print(f"\nUser: {user_input}")
        message = Content(role="user", parts=[Part.from_text(text=user_input)])
        
        async for event in runner.run_async(user_id="test_user", session_id="test_session", new_message=message):
            if hasattr(event, 'text') and event.text:
                print(f"Agent: {event.text}")
            elif hasattr(event, 'content') and event.content:
                print(f"Agent: {event.content}")
                
    print("\nScenario complete.")

if __name__ == "__main__":
    asyncio.run(run_scenario())
