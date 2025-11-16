from app.agents.background_finder_agent.subagents import (
    formatter_agent,
    search_agent,
)

from google.adk.agents import SequentialAgent

background_finder_agent = SequentialAgent(
    name="background_finder_agent",
    description="A background finder agent that finds the public X (formerly Twitter), LinkedIn, Facebook, and Doximity accounts of a given person who currently works or has worked at Yale University.",
    sub_agents=[search_agent, formatter_agent],
)