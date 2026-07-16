import asyncio
from google import genai
from google.genai.types import LiveConnectConfig, Modality

client = genai.Client(vertexai=True)

async def test():
    try:
        async with client.aio.live.connect(
            model='gemini-2.0-flash-exp', 
            config=LiveConnectConfig(response_modalities=[Modality.TEXT])
        ) as session:
            print("Connected.")
            await session.send(input="hi")
            async for msg in session.receive():
                print(f"Raw: {msg}")
                break
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
