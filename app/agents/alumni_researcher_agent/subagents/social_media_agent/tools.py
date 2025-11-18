"""Tools for the social media agent to search for candidate links."""

from google.adk.tools.tool_context import ToolContext
from app.utils.search_utils import search_social_media_profiles
from app.configs.llms import SOCIAL_MEDIA_MAX_LINKS


def search_social_media_candidates_tool(
    tool_context: ToolContext,
    alumni_name: str,
) -> dict:
    """
    Search for social media candidate links for a given alumni name.
    
    This tool searches across multiple platforms (X/Twitter, LinkedIn, Doximity,
    Google Scholar, Facebook) and returns candidate links in markdown format.
    
    Args:
        tool_context: Context for accessing session state
        alumni_name: Full name of the alumni to search for
        
    Returns:
        dict: A dictionary containing the search results in markdown format
    """
    try:
        # Run the search utility with max_links from config
        social_media_markdown = search_social_media_profiles(
            full_name=alumni_name,
            max_links=SOCIAL_MEDIA_MAX_LINKS,
        )
        
        return {
            "action": "search_social_media_candidates",
            "alumni_name": alumni_name,
            "message": f"Successfully searched for social media profiles for {alumni_name}",
            "candidate_links_markdown": social_media_markdown,
        }
    except Exception as e:
        return {
            "action": "search_social_media_candidates",
            "alumni_name": alumni_name,
            "message": f"Error searching for social media profiles: {str(e)}",
            "candidate_links_markdown": "",
        }

