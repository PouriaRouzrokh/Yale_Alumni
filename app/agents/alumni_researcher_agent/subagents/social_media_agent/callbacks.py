"""Callbacks for the social media agent to manage state with search utility results."""

from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from app.configs.app import logger


def before_social_media_agent_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    """
    Callback that runs before the social media agent executes.
    
    Note: The social media candidate links are already populated in the state
    before the root agent is called (in main.py). This callback just logs
    that the social media agent is about to run.
    
    Args:
        callback_context: Contains state and context information
        
    Returns:
        None to continue with normal agent processing
    """
    state = callback_context.state
    agent_name = callback_context.agent_name
    
    # Only process if this is the social_media_agent
    if agent_name != "social_media_agent":
        return None
    
    logger.info(f"[CALLBACK] Before social_media_agent: Checking state")
    
    # Verify that candidate links are in state (they should be set before root agent is called)
    candidate_links = state.get("social_media_candidate_links")
    if candidate_links:
        logger.info(
            f"[CALLBACK] Social media candidate links found in state "
            f"(length: {len(candidate_links)} chars)"
        )
    else:
        logger.warning(
            "[CALLBACK] No social_media_candidate_links found in state. "
            "Social media agent will not have candidate links."
        )
    
    return None


def after_social_media_agent_callback(
    callback_context: CallbackContext
) -> Optional[types.Content]:
    """
    Callback that runs after the social media agent executes.
    
    Note: We do not delete or modify state in this callback.
    State data persists for the entire session.
    
    Args:
        callback_context: Contains state and context information
        
    Returns:
        None to continue with normal agent processing
    """
    # No state cleanup needed - state persists for the session
    return None

