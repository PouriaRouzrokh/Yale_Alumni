from typing import List, Optional
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from .prompts import FORMATTER_AGENT_PROMPT
from app.configs.llms import BF_FORMATTER_MODEL
from app.configs.llms import BF_FORMATTER_MODEL_THINKING_BUDGET 
from google.adk.planners import BuiltInPlanner
from google.genai import types

class AccountInfo(BaseModel):
    account_type: str = Field(description="Type of account (e.g., X, LinkedIn, Facebook, Doximity, Google Scholar)")
    account_url: str = Field(description="URL of the account. Use empty string if not found.")

class BackgroundFinderOutputSchema(BaseModel):
    """Schema for comprehensive background information about Yale University medical alumni."""
    accounts: List[AccountInfo] = Field(
        description="List of exactly 5 accounts in order: X (Twitter), LinkedIn, Facebook, Doximity, Google Scholar. Each account must have account_type and account_url fields."
    )
    subspecialties: List[str] = Field(
        default_factory=list,
        description="List of medical subspecialties for the person. Empty list if none found."
    )
    current_practice_location: str = Field(
        default="",
        description="Current practice location in format 'Country, State, City' (e.g., 'United States, California, Los Angeles'). Empty string if not found."
    )
    current_practice_name: str = Field(
        default="",
        description="Name of the current practice/hospital/clinic. Empty string if not found."
    )
    current_practice_url: str = Field(
        default="",
        description="Website URL of the current practice. Empty string if not found."
    )
    current_practice_email: str = Field(
        default="",
        description="Email address of the current practice. Empty string if not found."
    )
    in_current_practice_since: Optional[str] = Field(
        default=None,
        description="Year (as string) when the person started at their current practice. None if not found."
    )
    additional_information: str = Field(
        default="",
        description="Any additional relevant professional information such as awards, publications, certifications, etc. Empty string if none."
    )

# Define the planner
planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(thinking_budget=BF_FORMATTER_MODEL_THINKING_BUDGET)
)

formatter_agent = LlmAgent(
    model=BF_FORMATTER_MODEL,
    name="formatter_agent",
    description="A formatter agent that formats comprehensive professional information about Yale University medical alumni into structured output.",
    instruction=FORMATTER_AGENT_PROMPT,
    output_schema=BackgroundFinderOutputSchema,
    planner=planner,
)