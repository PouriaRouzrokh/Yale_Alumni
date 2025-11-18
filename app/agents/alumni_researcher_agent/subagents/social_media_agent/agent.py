from google.adk.agents import LlmAgent
from app.configs.llms import SOCIAL_MEDIA_MODEL
from app.configs.llms import SOCIAL_MEDIA_MODEL_THINKING_BUDGET
from .prompts import SOCIAL_MEDIA_AGENT_PROMPT
from .tools import search_social_media_candidates_tool
from google.adk.planners import BuiltInPlanner
from google.genai import types

# Define the planner
planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(thinking_budget=SOCIAL_MEDIA_MODEL_THINKING_BUDGET)
)

social_media_agent = LlmAgent(
    model=SOCIAL_MEDIA_MODEL,
    name="social_media_agent",
    description="A social media profile identification agent that selects the most appropriate social media profile links for Yale University medical alumni from candidate search results.",
    instruction=SOCIAL_MEDIA_AGENT_PROMPT,
    tools=[search_social_media_candidates_tool],
    planner=planner,
)

