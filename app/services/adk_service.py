import uuid
import json
import time
from typing import Optional, Dict, Any, Tuple
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.runners import Runner
from app.configs.app import APP_NAME, logger
from app.configs.database import SQLALCHEMY_DATABASE_URL
from app.agents.agent_factory import get_root_agent, AgentMode
from app.utils.agent_utils import call_root_agent_async
from app.agents.background_finder_agent.subagents.formatter_agent import BackgroundFinderOutputSchema


class ADKService:
    """Service for managing Google ADK sessions and AI agent interactions."""

    def __init__(self, user_id: str, agent_mode: AgentMode = "background_finder") -> None:
        """
        Initialize ADK service with user_id and agent_mode.
        Creates session and runner once during initialization.
        
        Args:
            user_id: User identifier
            agent_mode: Agent mode to use
        """
        try:
            self.session_service = DatabaseSessionService(
                db_url=SQLALCHEMY_DATABASE_URL
            )
        except Exception as e:
            logger.error(f"Error initializing session service: {e}")
            self.session_service = InMemorySessionService()

        self.user_id = user_id
        self.agent_mode = agent_mode
        
        # These will be set by initialize() method
        self.runner: Optional[Runner] = None
        self.session_id: Optional[str] = None

    async def initialize(self) -> None:
        """Create session and runner. Must be called after __init__."""
        # Create session
        self.session_id = str(uuid.uuid4())
        initial_state = {}
        
        session = await self.session_service.create_session(
            app_name=APP_NAME,
            user_id=self.user_id,
            session_id=self.session_id,
            state=initial_state,
        )
        
        # Create runner
        root_agent = get_root_agent(self.agent_mode)
        self.runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=self.session_service,
        )
        
        logger.info(f"Initialized ADKService: user_id={self.user_id}, agent_mode={self.agent_mode}, session_id={self.session_id}")

    async def get_agent_response(
        self, 
        query: str
    ) -> Tuple[Optional[BackgroundFinderOutputSchema], Optional[Dict[str, Any]]]:
        """
        Get the response from the agent and parse it into structured format.
        Uses the runner and session created during initialization.
        
        Args:
            query: User's query string
            
        Returns:
            Tuple of (parsed_response, token_counts) or (None, None) on error
        """
        if self.runner is None or self.session_id is None:
            raise ValueError("ADKService not initialized. Call initialize() first.")
        
        start_time = time.time()

        try: 
            logger.info(f"Calling root agent in mode: {self.agent_mode}")
            response_text, token_counts = await call_root_agent_async(
                runner=self.runner,
                user_id=self.user_id,
                session_id=self.session_id,
                query=query,
            )
            
            if not response_text:
                logger.warning("No response text received from agent")
                return None, token_counts
            
            # Parse JSON response into Pydantic model
            # Note: agent_utils.py extracts the raw text from event.content.parts[0].text
            # We handle the JSON parsing here to convert it into the structured schema
            try:
                response_text = response_text.strip()
                
                # Check if response looks like JSON (should start with '{' for structured output)
                if not response_text.startswith('{'):
                    # Try to find JSON object in the response (in case there's extra text)
                    json_start = response_text.find('{')
                    if json_start >= 0:
                        json_end = response_text.rfind('}') + 1
                        if json_end > json_start:
                            response_text = response_text[json_start:json_end]
                        else:
                            raise ValueError("No valid JSON object found in response")
                    else:
                        raise ValueError(f"Response does not contain valid JSON. Response starts with: {response_text[:100]}")
                
                # Parse JSON string into dictionary
                parsed_data = json.loads(response_text)
                
                # Validate and parse into Pydantic model
                parsed_response = BackgroundFinderOutputSchema(**parsed_data)
                
                elapsed_time = time.time() - start_time
                logger.info(f"Root agent completed successfully in {elapsed_time:.2f} seconds")
                logger.info(f"Total tokens used: {token_counts.get('total_token_count', 0)}")
                return parsed_response, token_counts
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
                return None, token_counts
            except ValueError as e:
                logger.error(f"Invalid response format: {e}")
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
                return None, token_counts
            except Exception as parse_error:
                logger.error(f"Failed to parse response into schema: {parse_error}")
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None, token_counts
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error getting agent response: {e}")
            return None, None