import asyncio
from google import genai
from google.genai.types import LiveConnectConfig, Modality, Content, Part

client = genai.Client(vertexai=True)

async def test():
    try:
        async with client.aio.live.connect(
            model='gemini-live-2.5-flash-native-audio', 
            config=LiveConnectConfig(response_modalities=[Modality.TEXT])
        ) as session:
            print("Connected.")
            await session.send(input=Content(role='user', parts=[Part.from_text(text='hi')]))
            async for msg in session.receive():
                print(f"Raw: {msg}")
                break
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
