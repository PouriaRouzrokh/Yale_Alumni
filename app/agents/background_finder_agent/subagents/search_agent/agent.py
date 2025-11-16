from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from .prompts import SEARCH_AGENT_PROMPT
from app.configs.llms import BF_SEARCH_MODEL
from app.configs.llms import BF_SEARCH_MODEL_THINKING_BUDGET
from google.adk.planners import BuiltInPlanner
from google.genai import types

# Define the planner
planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(thinking_budget=BF_SEARCH_MODEL_THINKING_BUDGET)
)

search_agent = LlmAgent(
    model=BF_SEARCH_MODEL,
    name="search_agent",
    description="A comprehensive search agent that finds detailed professional and academic information about Yale University medical alumni, including social media profiles, practice information, subspecialties, and additional professional details.",
    instruction=SEARCH_AGENT_PROMPT,
    tools=[google_search],
    planner=planner,
)