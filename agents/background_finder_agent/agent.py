import dotenv

dotenv.load_dotenv()

from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="background_finder_agent",
    instruction="You are a background finder agent. You are given a user query and you need to find the background information for the user.",
    model="gemini-2.0-flash",
)