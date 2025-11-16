# Background finder sub-agents models

BF_SEARCH_MODEL = "gemini-2.5-flash"
BF_SEARCH_MODEL_THINKING_BUDGET = 2048  # Higher budget for content generation + HTML formatting + URL analysis

BF_CRITIQUE_MODEL = "gemini-2.5-flash"
BF_CRITIQUE_MODEL_THINKING_BUDGET = 1024  # Smart bypass capability reduces actual usage

BF_FORMATTER_MODEL = "gemini-2.5-flash"
BF_FORMATTER_MODEL_THINKING_BUDGET = 1024  # HTML formatting only

# Email finder sub-agents models

EF_SEARCH_MODEL = "gemini-2.5-flash"
EF_SEARCH_MODEL_THINKING_BUDGET = 2048  # Higher budget for content generation + HTML formatting + URL analysis

EF_CRITIQUE_MODEL = "gemini-2.5-flash"
EF_CRITIQUE_MODEL_THINKING_BUDGET = 1024  # Smart bypass capability reduces actual usage

EF_FORMATTER_MODEL = "gemini-2.5-flash"
EF_FORMATTER_MODEL_THINKING_BUDGET = 1024  # HTML formatting only