import asyncio
from google.adk.runners import InMemoryRunner
from agent import root_agent
from google.genai import types

async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="hello_codeassist")
    session = await runner.session_service.create_session(app_name="hello_codeassist", user_id="u1")

    content = types.Content(role='user', parts=[types.Part.from_text(text='Say hi in one short sentence.')])

    texts = []
    async for event in runner.run_async(user_id="u1", session_id=session.id, new_message=content):
        if event.content and event.content.parts and event.content.parts[0].text:
            texts.append(event.content.parts[0].text)
    print("".join(texts))

if __name__ == "__main__":
    asyncio.run(main())
