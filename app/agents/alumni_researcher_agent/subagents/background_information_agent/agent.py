from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from .prompts import BACKGROUND_INFORMATION_AGENT_PROMPT
from app.configs.llms import BACKGROUND_INFORMATION_MODEL
from app.configs.llms import BACKGROUND_INFORMATION_MODEL_THINKING_BUDGET
from google.adk.planners import BuiltInPlanner
from google.genai import types

# Define the planner
planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(thinking_budget=BACKGROUND_INFORMATION_MODEL_THINKING_BUDGET)
)

background_information_agent = LlmAgent(
    model=BACKGROUND_INFORMATION_MODEL,
    name="background_information_agent",
    description="A specialized background information agent that finds current practice information for Yale University medical alumni, including practice URLs and detailed narratives about their post-Yale career.",
    instruction=BACKGROUND_INFORMATION_AGENT_PROMPT,
    tools=[google_search],
    planner=planner,
)