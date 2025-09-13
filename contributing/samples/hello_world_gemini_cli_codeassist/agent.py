from google.adk.agents import Agent
from google.adk.models import GeminiCLICodeAssist

# A minimal agent using the CodeAssist-backed Gemini provider
root_agent = Agent(
    model=GeminiCLICodeAssist(model="gemini-2.5-flash"),
    name="hello_codeassist_agent",
    description="Simple hello world with CodeAssist-backed Gemini",
    instruction="You are a helpful assistant."
)
