from typing import Literal
from app.agents.background_finder_agent.agent import background_finder_agent
# from app.agents.email_finder_agent.agent import email_finder_agent

AgentMode = Literal["background_finder", "email_finder"]

def get_root_agent(mode: AgentMode = "background_finder"):
    """
    Get the appropriate root agent based on the specified mode.
    
    Args:
        mode: The agent mode to use. Can be "fast" or "slow". Defaults to "fast".
    
    Returns:
        The appropriate root agent for the specified mode.
    
    Raises:
        ValueError: If an invalid mode is specified.
    """
    # Normalize mode names for flexibility
    normalized_mode = mode.lower().strip()
    
    if normalized_mode in ["background_finder"]:
        return background_finder_agent
    elif normalized_mode in ["email_finder"]:
        raise NotImplementedError("Email finder agent is not implemented yet.")
    else:
        raise ValueError(
            f"Invalid agent mode: {mode}. Supported modes: 'background_finder', 'email_finder'"
        )