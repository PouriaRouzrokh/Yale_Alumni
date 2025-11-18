"""Search utilities for finding social media profiles using DDGS."""

import logging
from typing import Dict, List, Optional
from ddgs import DDGS

logger = logging.getLogger(__name__)


# Define social media platforms and their URL patterns
SOCIAL_MEDIA_PLATFORMS = {
    "X (Twitter)": {
        "search_name": "X (Twitter)",
        "url_patterns": ["twitter.com", "x.com"],
    },
    "LinkedIn": {
        "search_name": "LinkedIn",
        "url_patterns": ["linkedin.com"],
    },
    "Doximity": {
        "search_name": "Doximity",
        "url_patterns": ["doximity.com"],
    },
    "Google Scholar": {
        "search_name": "Google Scholar",
        "url_patterns": ["scholar.google.com", "scholar.google"],
    },
    "Facebook": {
        "search_name": "Facebook",
        "url_patterns": ["facebook.com"],
    },
}


def _matches_platform(url: str, platform_patterns: List[str]) -> bool:
    """
    Check if a URL matches any of the platform's URL patterns.
    
    Args:
        url: The URL to check
        platform_patterns: List of URL patterns to match against
        
    Returns:
        True if the URL matches any pattern, False otherwise
    """
    url_lower = url.lower()
    return any(pattern.lower() in url_lower for pattern in platform_patterns)


def _search_platform(
    ddgs: DDGS,
    full_name: str,
    platform_name: str,
    max_results: int,
) -> List[Dict[str, str]]:
    """
    Search for a person's profile on a specific social media platform.
    
    Args:
        ddgs: DDGS instance for searching
        full_name: Full name of the person to search for
        platform_name: Name of the social media platform
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing title, href, and body for matching results
    """
    # Construct search query
    query = f"{full_name}, radiology, {platform_name}"
    logger.info(f"Searching for: {query}")
    
    matching_results = []
    platform_config = SOCIAL_MEDIA_PLATFORMS[platform_name]
    url_patterns = platform_config["url_patterns"]
    
    try:
        results = ddgs.text(query, max_results=max_results)
        
        for result in results:
            href = result.get("href", "")
            
            # Check if this result matches the platform's URL pattern
            if _matches_platform(href, url_patterns):
                matching_results.append({
                    "title": result.get("title", ""),
                    "href": href,
                    "body": result.get("body", ""),
                })
                
        logger.info(
            f"Found {len(matching_results)} matching results for {platform_name}"
        )
        
    except Exception as e:
        logger.error(f"Error searching for {platform_name}: {e}")
    
    return matching_results


def search_social_media_profiles(
    full_name: str,
    max_links: int = 20,
) -> str:
    """
    Search for a person's social media profiles across multiple platforms.
    
    This function searches for the given person's name across five social media
    platforms (X/Twitter, LinkedIn, Doximity, Google Scholar, and Facebook) and
    returns a markdown-formatted report with categorized links.
    
    Args:
        full_name: Full name of the person to search for
        max_links: Maximum number of search results to collect per platform
                  (default: 20)
        
    Returns:
        A markdown-formatted string containing categorized links by platform
    """
    logger.info(f"Starting social media search for: {full_name}")
    
    # Initialize DDGS
    ddgs = DDGS()
    
    # Dictionary to store results by platform
    results_by_platform: Dict[str, List[Dict[str, str]]] = {}
    
    # Search each platform
    for platform_name in SOCIAL_MEDIA_PLATFORMS.keys():
        logger.info(f"Searching {platform_name}...")
        results = _search_platform(
            ddgs=ddgs,
            full_name=full_name,
            platform_name=platform_name,
            max_results=max_links,
        )
        results_by_platform[platform_name] = results
    
    # Generate markdown report
    markdown_lines = [
        f"# Social Media Profile Search Results for {full_name}",
        "",
        f"**Search Parameters:**",
        f"- Name: {full_name}",
        f"- Maximum results per platform: {max_links}",
        "",
        "---",
        "",
    ]
    
    # Add results for each platform
    for platform_name, results in results_by_platform.items():
        markdown_lines.append(f"## {platform_name}")
        markdown_lines.append("")
        
        if results:
            markdown_lines.append(f"**Found {len(results)} matching link(s):**")
            markdown_lines.append("")
            
            for idx, result in enumerate(results, 1):
                title = result.get("title", "No title")
                href = result.get("href", "")
                body = result.get("body", "")
                
                markdown_lines.append(f"### {idx}. {title}")
                markdown_lines.append(f"")
                markdown_lines.append(f"**URL:** {href}")
                markdown_lines.append(f"")
                if body:
                    markdown_lines.append(f"**Description:** {body}")
                    markdown_lines.append(f"")
                markdown_lines.append("---")
                markdown_lines.append("")
        else:
            markdown_lines.append("*No matching links found.*")
            markdown_lines.append("")
        
        markdown_lines.append("")
    
    # Add summary
    total_links = sum(len(results) for results in results_by_platform.values())
    markdown_lines.append("## Summary")
    markdown_lines.append("")
    markdown_lines.append(f"**Total links found:** {total_links}")
    markdown_lines.append("")
    markdown_lines.append("**Breakdown by platform:**")
    for platform_name, results in results_by_platform.items():
        markdown_lines.append(f"- {platform_name}: {len(results)} link(s)")
    
    return "\n".join(markdown_lines)

