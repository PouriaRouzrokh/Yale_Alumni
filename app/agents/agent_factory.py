from typing import Literal
from app.agents.alumni_researcher_agent.agent import alumni_researcher_agent
# from app.agents.email_finder_agent.agent import email_finder_agent

AgentMode = Literal["alumni_researcher", "email_finder"]

def get_root_agent(mode: AgentMode = "alumni_researcher"):
    """
    Get the appropriate root agent based on the specified mode.
    
    Args:
        mode: The agent mode to use. Can be "alumni_researcher" or "email_finder". Defaults to "alumni_researcher".
    
    Returns:
        The appropriate root agent for the specified mode.
    
    Raises:
        ValueError: If an invalid mode is specified.
    """
    # Normalize mode names for flexibility
    normalized_mode = mode.lower().strip()
    
    if normalized_mode in ["alumni_researcher"]:
        return alumni_researcher_agent
    elif normalized_mode in ["email_finder"]:
        raise NotImplementedError("Email finder agent is not implemented yet.")
    else:
        raise ValueError(
            f"Invalid agent mode: {mode}. Supported modes: 'alumni_researcher', 'email_finder'"
        )