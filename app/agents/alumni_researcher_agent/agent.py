from app.agents.alumni_researcher_agent.subagents import (
    formatter_agent,
    background_information_agent,
    social_media_agent,
)

from google.adk.agents import SequentialAgent

# Create sequential agent: first collect background information, then identify social media links, then format the results
alumni_researcher_agent = SequentialAgent(
    name="alumni_researcher_agent",
    description="An alumni researcher agent that finds current practice information for Yale University medical alumni, identifies their social media profiles, and formats it into structured output.",
    sub_agents=[background_information_agent, social_media_agent, formatter_agent],
)