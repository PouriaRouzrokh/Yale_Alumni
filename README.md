# Yale Alumni Assistant

A multi-agent AI system built with Google's Agent Development Kit (ADK) that researches and compiles comprehensive professional information about Yale University medical alumni, specifically those from the Department of Radiology and Biomedical Imaging.

## Overview

This project automates the research process for Yale Radiology alumni by:
- Finding current practice information (institutions, URLs, narratives)
- Identifying social media profiles across five platforms
- Formatting all information into structured output
- Generating CSV reports with comprehensive alumni data

The system uses a sequential multi-agent architecture where specialized agents work together to gather, validate, and structure information about each alumnus/alumna.

## Architecture

### Agent Pipeline

The system uses a **Sequential Agent** architecture where three specialized sub-agents execute in order, with each agent's output feeding into the next:

```
User Query (Alumni Name + Year)
    |
    v
+-------------------------------------------+
|  Alumni Researcher Agent (Sequential)     |
|                                           |
|  1. Background Information Agent          |
|     |                                     |
|     v                                     |
|  2. Social Media Agent                    |
|     |                                     |
|     v                                     |
|  3. Formatter Agent                       |
+-------------------------------------------+
    |
    v
Structured Output (Pydantic Schema)
    |
    v
CSV Report
```

### Agent Interactions

#### 1. Background Information Agent
**Purpose**: Research current practice information for Yale Radiology alumni

**Capabilities**:
- Searches for current practices (academic institutions, private practices, research institutions)
- Identifies practice names, URLs, and locations
- Extracts detailed narratives about post-Yale career activities
- Collects additional professional information (awards, publications, certifications)
- Deduplicates practices even when they appear with different names

**Tools**:
- `google_search`: Performs web searches to find practice information

**Output**: Unstructured text containing:
- Practice names (comma-separated or listed)
- Practice URLs (comma-separated or listed)
- Comprehensive narrative about practices
- Additional professional information

**Key Features**:
- Optimized to make a single comprehensive search call when possible
- Focuses on CURRENT practices only (not past positions)
- Carefully deduplicates practices with different naming variations

#### 2. Social Media Agent
**Purpose**: Identify and validate social media profile links for the alumni

**Capabilities**:
- Searches for candidate links across five platforms:
  - X (Twitter) - `twitter.com` or `x.com`
  - LinkedIn - `linkedin.com`
  - Doximity - `doximity.com`
  - Google Scholar - `scholar.google.com`
  - Facebook - `facebook.com`
- Evaluates candidate links based on:
  - Name matching (most important factor)
  - Background information from previous agent (if available)
  - Professional context (radiology-related content)
  - Evidence against validity (different profession, wrong person)
- Selects the most appropriate link for each platform

**Tools**:
- `search_social_media_candidates_tool`: Searches for candidate links using DDGS (DuckDuckGo Search)

**Input**: 
- Receives output from Background Information Agent
- Uses alumni name from user query

**Output**: Structured text with selected links:
```
X (Twitter): [URL or empty]
LinkedIn: [URL or empty]
Doximity: [URL or empty]
Google Scholar: [URL or empty]
Facebook: [URL or empty]
```

**Key Features**:
- **Never hallucinates links** - only selects from candidate links returned by the search tool
- Relaxed validation criteria - doesn't require extensive background information
- Can work with just name and radiology context if background info is sparse
- Prioritizes links with most evidence FOR validity and least evidence AGAINST validity

#### 3. Formatter Agent
**Purpose**: Structure and format all collected information into a standardized output schema

**Capabilities**:
- Parses unstructured output from Background Information Agent
- Extracts social media links from Social Media Agent output
- Formats practice information into comma-separated lists
- Creates unified narrative covering all practices
- Validates and structures all data according to Pydantic schema

**Output Schema** (`AlumniResearcherOutputSchema`):
```python
{
    "current_practices_names": str,        # Comma-separated practice names
    "current_practices_urls": str,          # Comma-separated practice URLs
    "current_practice_narrative": str,     # Unified narrative about practices
    "additional_information": str,          # Non-practice professional info
    "x_twitter_link": str,                  # X/Twitter profile URL
    "linkedin_link": str,                   # LinkedIn profile URL
    "doximity_link": str,                   # Doximity profile URL
    "google_scholar_link": str,             # Google Scholar profile URL
    "facebook_link": str                    # Facebook profile URL
}
```

**Key Features**:
- Ensures practice names and URLs lists have matching lengths
- Deduplicates practices
- Creates single unified narrative (not separate per practice)
- Handles missing information gracefully (empty strings)

## Data Flow

### Session Management

The system uses Google ADK's session management:
- **Runner**: Created once during initialization, reused for all queries
- **Sessions**: A new session is created for each alumni name processed
- **State**: Each session maintains its own state, allowing agents to pass information sequentially

### Processing Flow

1. **Input**: CSV file (`data/residents_base_info.csv`) containing:
   - First Name
   - Last Name
   - Entry Year

2. **Query Construction**: For each row:
   ```
   query = f"alumni name: {First Name} {Last Name}, year of entry: {Entry Year}"
   ```

3. **Agent Execution**:
   - New session created
   - Sequential agent pipeline executes:
     - Background Information Agent -> Social Media Agent -> Formatter Agent
   - Each agent's output becomes input for the next

4. **Output Parsing**:
   - Formatter Agent returns structured JSON
   - Parsed into `AlumniResearcherOutputSchema` Pydantic model
   - Token usage tracked and accumulated

5. **CSV Generation**:
   - Results compiled into DataFrame
   - Columns include:
     - Name, Year of Entry
     - Practice information (names, URLs, narrative)
     - Additional information
     - Social media links (5 platforms)
     - Token usage statistics

## Project Structure

```
Yale_Alumni/
├── app/
│   ├── agents/
│   │   ├── agent_factory.py          # Agent factory for mode selection
│   │   └── alumni_researcher_agent/
│   │       ├── agent.py              # Sequential agent definition
│   │       └── subagents/
│   │           ├── background_information_agent/
│   │           │   ├── agent.py      # Background info agent
│   │           │   └── prompts.py    # Agent instructions
│   │           ├── social_media_agent/
│   │           │   ├── agent.py      # Social media agent
│   │           │   ├── prompts.py   # Agent instructions
│   │           │   ├── tools.py      # Search tool definition
│   │           │   └── callbacks.py  # (Currently unused)
│   │           └── formatter_agent/
│   │               ├── agent.py       # Formatter agent + schema
│   │               └── prompts.py    # Agent instructions
│   ├── configs/
│   │   ├── app.py                    # Application configuration
│   │   ├── database.py               # Database configuration
│   │   └── llms.py                   # LLM models & settings
│   ├── services/
│   │   └── adk_service.py            # ADK session & runner management
│   ├── utils/
│   │   ├── agent_utils.py           # Agent calling utilities
│   │   ├── cmd_utils.py             # Command-line utilities
│   │   └── search_utils.py          # DDGS search implementation
│   └── main.py                      # Main execution script
├── data/
│   ├── residents_base_info.csv      # Input CSV
│   ├── alumni_results.csv            # Output CSV
│   └── database.db                  # ADK session database
├── pyproject.toml                   # Project dependencies
└── README.md                        # This file
```

## Key Components

### Search Utilities (`app/utils/search_utils.py`)

The `search_social_media_profiles` function:
- Uses DDGS (DuckDuckGo Search) to search across five platforms
- Constructs queries: `"{full_name}, radiology, {platform_name}"`
- Programmatically filters results by URL patterns
- Returns markdown-formatted candidate links

**Configuration**: `SOCIAL_MEDIA_MAX_LINKS` in `app/configs/llms.py` controls maximum results per platform (default: 20)

### ADK Service (`app/services/adk_service.py`)

Manages the lifecycle of ADK components:
- **Initialization**: Creates runner once (reused for all queries)
- **Session Management**: Creates new session per query
- **Response Parsing**: Converts JSON response to Pydantic schema
- **Token Tracking**: Accumulates token usage across all events

### Configuration (`app/configs/llms.py`)

Centralized configuration for:
- **LLM Models**: Each agent uses `gemini-2.5-flash`
- **Thinking Budgets**: Token budgets for agent reasoning
  - Background Information: 2048 tokens
  - Social Media: 2048 tokens
  - Formatter: 1024 tokens
- **Search Settings**: `SOCIAL_MEDIA_MAX_LINKS = 20`

## Usage

### Prerequisites

1. **Python 3.13+**
2. **UV Package Manager** (project uses UV for dependency management)
3. **Environment Variables**: Create a `.env` file with:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### Installation

```bash
# Install dependencies using UV
uv sync

# Or install manually
uv pip install -e .
```

### Running the Pipeline

```bash
# Run the main script
uv run python app/main.py
```

The script will:
1. Load alumni data from `data/residents_base_info.csv`
2. Process each row (currently limited to first 10 rows)
3. Execute the agent pipeline for each alumni
4. Save results to `data/alumni_results.csv`

### Configuration

Edit `app/configs/llms.py` to adjust:
- LLM models for each agent
- Thinking budgets (token limits)
- Maximum search results per platform

## Agent Communication Patterns

### Sequential Data Flow

1. **Background Information Agent** -> **Social Media Agent**:
   - Background agent's output is automatically passed as context
   - Social media agent can reference practice information, locations, etc.
   - If background info is sparse, social media agent still proceeds

2. **Social Media Agent** -> **Formatter Agent**:
   - Social media agent's structured output is passed as context
   - Formatter agent extracts links from the structured format
   - Formatter agent also receives background agent's output (from conversation history)

### Tool Usage

- **Background Information Agent**: Uses `google_search` tool directly
- **Social Media Agent**: Uses `search_social_media_candidates_tool` which wraps `search_social_media_profiles`
- **Formatter Agent**: No tools - only formats existing information

### State Management

- Each session maintains conversation history
- Agents can access previous agent outputs through conversation context
- No explicit state manipulation needed - ADK handles context passing automatically

## Output Format

The final CSV includes:

**Practice Information**:
- `Current Practices Names`: Comma-separated list
- `Current Practices URLs`: Comma-separated list (matching order)
- `Current Practice Narrative`: Unified narrative text
- `Additional Information`: Non-practice professional info

**Social Media Links**:
- `X (Twitter) Link`
- `LinkedIn Link`
- `Doximity Link`
- `Google Scholar Link`
- `Facebook Link`

**Metadata**:
- `Name`
- `Year of Entry to Yale`
- Token usage statistics (total, prompt, candidates, cached, thoughts)

## Error Handling

- Individual alumni processing errors are caught and logged
- Failed rows include error messages in the CSV
- Token tracking continues even if parsing fails
- Empty strings used for missing information (never null values)

## Future Enhancements

- Email finder agent (placeholder exists in `agent_factory.py`)
- Additional social media platforms
- Enhanced validation and verification
- Batch processing optimizations
- API endpoint for programmatic access

## Dependencies

Key dependencies:
- `google-adk>=1.18.0`: Google Agent Development Kit
- `ddgs>=0.0.1`: DuckDuckGo Search library
- `pandas>=2.3.3`: Data manipulation
- `pydantic`: Data validation and schema

See `pyproject.toml` for complete dependency list.

## License

[Add license information here]

## Contributing

[Add contributing guidelines here]
