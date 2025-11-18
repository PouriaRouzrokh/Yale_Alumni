from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from .prompts import FORMATTER_AGENT_PROMPT
from app.configs.llms import FORMATTER_MODEL
from app.configs.llms import FORMATTER_MODEL_THINKING_BUDGET 
from google.adk.planners import BuiltInPlanner
from google.genai import types

class AlumniResearcherOutputSchema(BaseModel):
    """Schema for comprehensive background information about Yale University medical alumni."""
    current_practices_names: str = Field(
        default="",
        description="Comma-separated list of current practice names where the alumni is currently working or affiliated. Each practice name should be separated by a comma and space (e.g., 'Practice A, Practice B, Practice C'). Empty string if no practices found."
    )
    current_practices_urls: str = Field(
        default="",
        description="Comma-separated list of URLs corresponding to each practice in the same order as current_practices_names. Each URL should be separated by a comma and space. Use empty string for practices without URLs. Empty string if no practices found."
    )
    current_practice_narrative: str = Field(
        default="",
        description="A comprehensive summary narrative describing what the alumni has been doing after graduating from Yale Radiology, including their roles, responsibilities, activities, notable achievements, research, clinical work, and career progression. This should be a single unified narrative covering all their current practices. Empty string if not available."
    )
    additional_information: str = Field(
        default="",
        description="Any additional relevant professional information about what the alumni has done after graduation that is NOT related to their current practices. This includes awards, publications, certifications, notable achievements, or other professional activities outside of their practice work. Empty string if none."
    )
    x_twitter_link: str = Field(
        default="",
        description="Link to the alumni's X (Twitter) profile. Empty string if not found or not identified."
    )
    linkedin_link: str = Field(
        default="",
        description="Link to the alumni's LinkedIn profile. Empty string if not found or not identified."
    )
    doximity_link: str = Field(
        default="",
        description="Link to the alumni's Doximity profile. Empty string if not found or not identified."
    )
    google_scholar_link: str = Field(
        default="",
        description="Link to the alumni's Google Scholar profile. Empty string if not found or not identified."
    )
    facebook_link: str = Field(
        default="",
        description="Link to the alumni's Facebook profile. Empty string if not found or not identified."
    )

# Define the planner
planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(thinking_budget=FORMATTER_MODEL_THINKING_BUDGET)
)

formatter_agent = LlmAgent(
    model=FORMATTER_MODEL,
    name="formatter_agent",
    description="A formatter agent that formats comprehensive professional information about Yale University medical alumni into structured output.",
    instruction=FORMATTER_AGENT_PROMPT,
    output_schema=AlumniResearcherOutputSchema,
    planner=planner,
)