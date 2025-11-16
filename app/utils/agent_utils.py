"""Agent utility functions for processing and calling AI agents."""

from typing import Optional, List, Any
from google.genai import types

from app.utils.cmd_utils import display_system_message


import logging
from typing import Any, Optional

# Get logger
logger = logging.getLogger("Recally")


async def process_agent_message(event: Any) -> Optional[str]:
    """
    Process and log agent response events, returning text only from final events.

    Args:
        event: Agent response event containing content parts

    Returns:
        Extracted text content if event is final and has text, None otherwise
    """
    # Log basic event info
    logger.debug(f"Event ID: {event.id}, Author: {event.author}")

    # Check for specific parts and log them
    if logger.level == logging.DEBUG:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "executable_code") and part.executable_code:
                    # Log executable code
                    logger.debug(f"Agent generated code: {part.executable_code.code}")
                elif (
                    hasattr(part, "code_execution_result")
                    and part.code_execution_result
                ):
                    # Log code execution results
                    logger.debug(
                        f"Code Execution Result: {part.code_execution_result.outcome} - Output: {part.code_execution_result.output}"
                    )
                elif hasattr(part, "tool_response") and part.tool_response:
                    # Log tool responses
                    logger.debug(f"Tool Response: {part.tool_response.output}")
                elif hasattr(part, "function_call") and part.function_call:
                    # Log function calls
                    logger.debug(f"Function Call: {part.function_call.name}")
                elif hasattr(part, "function_response") and part.function_response:
                    # Log function responses
                    logger.debug(
                        f"Function Response: {part.function_response.response}"
                    )
                # Log any text parts found in any event for debugging
                elif hasattr(part, "text") and part.text and not part.text.isspace():
                    logger.debug(f"Text content: '{part.text.strip()}'")

    # Check for final response
    final_response = None
    if hasattr(event, "is_final_response") and event.is_final_response():
        logger.info("Final agent response detected")
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            logger.info(f"Final agent response text: {final_response[:100]}...")
        else:
            logger.warning("Final agent response detected but no text content found")
    else:
        logger.debug("Non-final event - no text returned")

    return final_response

def get_token_counts(event):
    """
    Extract token counts from an event object's usage_metadata.
    
    Args:
        event: Event object containing usage_metadata
        
    Returns:
        dict: Dictionary containing all token counts
    """
    try:
        usage_metadata = event.usage_metadata
        
        # Extract basic token counts
        token_counts = {
            'total_token_count': getattr(usage_metadata, 'total_token_count', 0),
            'prompt_token_count': getattr(usage_metadata, 'prompt_token_count', 0),
            'candidates_token_count': getattr(usage_metadata, 'candidates_token_count', 0),
            'cached_content_token_count': getattr(usage_metadata, 'cached_content_token_count', 0),
            'thoughts_token_count': getattr(usage_metadata, 'thoughts_token_count', 0)
        }
        
        # Extract cache tokens details
        if hasattr(usage_metadata, 'cache_tokens_details') and usage_metadata.cache_tokens_details:
            cache_tokens = {}
            for item in usage_metadata.cache_tokens_details:
                modality = item.modality.name if hasattr(item.modality, 'name') else str(item.modality)
                cache_tokens[modality.lower()] = item.token_count
            token_counts['cache_tokens_by_modality'] = cache_tokens
        
        # Extract prompt tokens details
        if hasattr(usage_metadata, 'prompt_tokens_details') and usage_metadata.prompt_tokens_details:
            prompt_tokens = {}
            for item in usage_metadata.prompt_tokens_details:
                modality = item.modality.name if hasattr(item.modality, 'name') else str(item.modality)
                prompt_tokens[modality.lower()] = item.token_count
            token_counts['prompt_tokens_by_modality'] = prompt_tokens
        
        return token_counts
        
    except AttributeError as e:
        # If the event doesn't have usage_metadata or expected structure
        return {'error': f'Could not extract token counts: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}


def process_user_message(
    message: str,
    images: Optional[List[Any]] = None,
    voice_notes: Optional[List[Any]] = None,
) -> types.Content:
    """
    Process a user message and create multimodal content with images and audio.

    Args:
        message: Text message from user
        images: List of image objects with original_image and mask_image attributes
        voice_notes: List of voice note objects with audio_data and format attributes

    Returns:
        Multimodal content with text, images, and audio parts
    """
    parts = [types.Part(text=message)]

    # Add images if provided
    if images:
        for img in images:
            if img.original_image:
                parts.append(
                    types.Part(
                        text=f"Image: {img.content_type}"
                    )
                )
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=f"{img.content_type}", data=img.original_image
                        )
                    )
                )
            if img.mask_image and img.has_occlusions:
                parts.append(
                    types.Part(
                        text=f"Mask image: {img.mask_content_type}"
                    )
                )
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=f"{img.mask_content_type}",
                            data=img.mask_image,
                        )
                    )
                )

    # Add voice notes if provided
    if voice_notes:
        for note in voice_notes:
            if note.audio_data:
                parts.append(
                    types.Part(
                        text=f"Voice note: {note.format}"
                    )
                )
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=(
                                f"audio/{note.format}" if note.format else "audio/mp4"
                            ),
                            data=note.audio_data,
                        )
                    )
                )

    return types.Content(role="user", parts=parts)


async def call_root_agent_async(
    runner: Any,
    user_id: str,
    session_id: str,
    query: str,
    images: Optional[List[Any]] = None,
    voice_notes: Optional[List[Any]] = None,
) -> tuple[Optional[str], dict]:
    """
    Call the root agent asynchronously with multimodal content.
    
    This function handles low-level event processing and text extraction.
    It does NOT parse JSON or convert responses to structured formats.
    For structured output parsing, see ADKService.get_agent_response().

    Args:
        runner: ADK runner instance
        user_id: User identifier
        session_id: Session identifier
        query: User's text query
        images: List of image objects
        voice_notes: List of voice note objects

    Returns:
        Tuple of (agent response text if available, accumulated token counts dict)
        The response text is raw text extracted from event.content.parts[0].text.
        For agents with output_schema, this will be JSON text that needs to be parsed
        by the caller (e.g., ADKService.get_agent_response()).
    """
    content = process_user_message(query, images, voice_notes)
    final_response_text = None
    
    # Initialize token count accumulators
    accumulated_token_counts = {
        'total_token_count': 0,
        'prompt_token_count': 0,
        'candidates_token_count': 0,
        'cached_content_token_count': 0,
        'thoughts_token_count': 0,
        'cache_tokens_by_modality': {},
        'prompt_tokens_by_modality': {}
    }
    
    # Track individual event token counts for API
    event_token_counts = []

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Get token counts for this event
            token_counts = get_token_counts(event)
            
            # Log individual event token counts
            if 'error' not in token_counts:
                event_token_counts.append({
                    'event_id': getattr(event, 'id', 'unknown'),
                    'author': getattr(event, 'author', 'unknown'),
                    'token_counts': token_counts
                })
                
                # Accumulate token counts
                for key in ['total_token_count', 'prompt_token_count', 'candidates_token_count', 
                           'cached_content_token_count', 'thoughts_token_count']:
                    if key in token_counts and token_counts[key] is not None:
                        accumulated_token_counts[key] += token_counts[key]
                
                # Accumulate modality-specific counts
                if 'cache_tokens_by_modality' in token_counts:
                    for modality, count in token_counts['cache_tokens_by_modality'].items():
                        accumulated_token_counts['cache_tokens_by_modality'][modality] = \
                            accumulated_token_counts['cache_tokens_by_modality'].get(modality, 0) + count
                
                if 'prompt_tokens_by_modality' in token_counts:
                    for modality, count in token_counts['prompt_tokens_by_modality'].items():
                        accumulated_token_counts['prompt_tokens_by_modality'][modality] = \
                            accumulated_token_counts['prompt_tokens_by_modality'].get(modality, 0) + count
                
                logger.debug(f"Event {getattr(event, 'id', 'unknown')} token counts: {token_counts}")
            
            # Process the agent message for final response
            response = await process_agent_message(event)

            if response:
                final_response_text = response
                
    except Exception as e:
        display_system_message(f"Error during agent call: {e}")

    # Add event-level details to accumulated counts for API response
    accumulated_token_counts['event_details'] = event_token_counts
    
    # Log final accumulated token counts
    logger.info(f"Total accumulated token counts: {accumulated_token_counts}")

    return final_response_text, accumulated_token_counts
