# Alumni Researcher Agent sub-agents models

# Background Information Agent
BACKGROUND_INFORMATION_MODEL = "gemini-2.5-flash"
BACKGROUND_INFORMATION_MODEL_THINKING_BUDGET = 2048  # Higher budget for content generation + HTML formatting + URL analysis

# Social Media Agent
SOCIAL_MEDIA_MODEL = "gemini-2.5-flash"
SOCIAL_MEDIA_MODEL_THINKING_BUDGET = 2048  # Link validation and selection
SOCIAL_MEDIA_MAX_LINKS = 20  # Maximum number of links to collect per platform

# Formatter Agent
FORMATTER_MODEL = "gemini-2.5-flash"
FORMATTER_MODEL_THINKING_BUDGET = 1024  # HTML formatting and structured output generation