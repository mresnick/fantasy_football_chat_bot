# Fantasy Football Chat Bot - Development Guide

## 🚀 Development Setup

### Prerequisites
- **Python 3.7+** (recommended: Python 3.9+)
- **Git** for version control
- **Docker** (optional, for containerized development)
- **Code Editor** (VS Code recommended with Python extension)

### Quick Start

#### Option 1: Local Python Development
```bash
# Clone the repository
git clone https://github.com/dtcarls/fantasy_football_chat_bot.git
cd fantasy_football_chat_bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-test.txt
```

#### Option 2: Docker Development
```bash
# Clone the repository
git clone https://github.com/dtcarls/fantasy_football_chat_bot.git
cd fantasy_football_chat_bot

# Build Docker image
docker build -t fantasy_football_chat_bot .

# Run with environment variables
docker run --rm \
  -e LEAGUE_ID=your_league_id \
  -e LEAGUE_YEAR=2024 \
  -e BOT_ID=your_bot_id \
  fantasy_football_chat_bot
```

## ⚙️ Configuration

### Environment Variables Setup

Create a `.env` file (not tracked in git) for local development:

```bash
# Required Variables
LEAGUE_ID=123456
LEAGUE_YEAR=2024
START_DATE=2024-09-03
END_DATE=2025-01-07
TIMEZONE=America/New_York

# Chat Platform Configuration (at least one required)
BOT_ID=your_groupme_bot_id
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Discord Bot (optional)
DISCORD_TOKEN=your_discord_bot_token
DISCORD_SERVER_ID=your_discord_server_id

# Private League Access (optional)
ESPN_S2=your_espn_s2_cookie
SWID=your_swid

# Feature Flags (optional)
TOP_HALF_SCORING=false
RANDOM_PHRASE=false
MONITOR_REPORT=true
WAIVER_REPORT=true
DAILY_WAIVER=false

# Messages (optional)
INIT_MSG=Fantasy Football Bot is ready!
```

### Loading Environment Variables
```python
# For local development with .env file
from dotenv import load_dotenv
load_dotenv()

# The project uses gamedaybot/espn/env_vars.py for configuration
from gamedaybot.espn.env_vars import get_env_vars
config = get_env_vars()
```

## 🧪 Testing Strategy

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gamedaybot

# Run specific test file
pytest tests/test_functionality.py

# Run with verbose output
pytest -v
```

### Test Structure
```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── test_discord.py      # Discord integration tests
├── test_groupme.py      # GroupMe integration tests  
├── test_slack.py        # Slack integration tests
├── test_utils.py        # Utility function tests
└── dry_run_all_functions.py  # Integration test runner
```

### Mock Testing Pattern
```python
# Example from tests/conftest.py
import pytest
import requests_mock

@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

# Usage in tests
def test_groupme_send_message(mock_requests):
    mock_requests.post('https://api.groupme.com/v3/bots/post')
    # Test GroupMe functionality
```

## 🛠️ Development Workflow

### Code Organization

#### Adding New Functionality
1. **Add core logic** to [`gamedaybot/espn/functionality.py`](../gamedaybot/espn/functionality.py)
2. **Register function** in [`gamedaybot/espn/espn_bot.py`](../gamedaybot/espn/espn_bot.py)
3. **Add to scheduler** in [`gamedaybot/espn/scheduler.py`](../gamedaybot/espn/scheduler.py) (if automated)
4. **Add Discord command** in [`gamedaybot/chat/discord_bot.py`](../gamedaybot/chat/discord_bot.py) (if interactive)
5. **Write tests** for the new functionality

#### Example: Adding a New Report Function

**Step 1**: Add function to `functionality.py`
```python
def get_weekly_mvp(league, week=None):
    """Get the MVP (highest scorer) for a given week"""
    if not week:
        week = league.current_week - 1
    
    box_scores = league.box_scores(week=week)
    highest_score = 0
    mvp_team = None
    
    for matchup in box_scores:
        if matchup.home_team and matchup.home_score > highest_score:
            highest_score = matchup.home_score
            mvp_team = matchup.home_team
        if matchup.away_team and matchup.away_score > highest_score:
            highest_score = matchup.away_score
            mvp_team = matchup.away_team
    
    return f"Week {week} MVP: {mvp_team.team_name} ({highest_score:.2f} points)"
```

**Step 2**: Register in `espn_bot.py`
```python
def espn_bot(function):
    # ... existing code ...
    
    elif function == "get_weekly_mvp":
        text = espn.get_weekly_mvp(league)
    
    # ... rest of function
```

**Step 3**: Add to scheduler (optional)
```python
def scheduler():
    # ... existing jobs ...
    
    sched.add_job(espn_bot, 'cron', ['get_weekly_mvp'], id='mvp',
                  day_of_week='tue', hour=8, minute=0, 
                  start_date=ff_start_date, end_date=ff_end_date,
                  timezone=my_timezone, replace_existing=True)
```

**Step 4**: Add Discord command
```python
@app_commands.command(description="Get the weekly MVP")
async def weekly_mvp(self, interaction, week: int = None):
    await interaction.response.send_message(
        self.codeblock(espn.get_weekly_mvp(self.league, week))
    )
```

## 🐛 Debugging & Development

### Local Development Run
```bash
# Run the bot locally (will run scheduler)
python gamedaybot/espn/espn_bot.py

# Test specific function
python -c "from gamedaybot.espn.espn_bot import espn_bot; espn_bot('get_scoreboard_short')"
```

### Debugging ESPN API Issues
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test ESPN connection
from espn_api.football import League
league = League(league_id=123456, year=2024)
print(f"League: {league.settings.name}")
print(f"Teams: {[team.team_name for team in league.teams]}")
```

### Common Development Issues

#### **Issue**: ESPN API Authentication
```python
# For private leagues, ensure ESPN_S2 and SWID are set
# Get these from browser cookies after logging into ESPN
import os
espn_s2 = os.environ.get('ESPN_S2')
swid = os.environ.get('SWID')
league = League(league_id=123456, year=2024, espn_s2=espn_s2, swid=swid)
```

#### **Issue**: Chat Platform Webhooks Not Working
```python
# Test webhook URLs directly
import requests
webhook_url = "your_webhook_url_here"
payload = {"text": "Test message"}
response = requests.post(webhook_url, json=payload)
print(f"Status: {response.status_code}, Response: {response.text}")
```

#### **Issue**: Timezone Conflicts
```python
# Ensure timezone is properly set
from gamedaybot.espn.env_vars import get_env_vars
config = get_env_vars()
print(f"Configured timezone: {config['my_timezone']}")

# Test scheduler with timezone
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler(timezone='America/New_York')
```

## 📁 File Structure & Navigation

### Core Files to Understand
- [`gamedaybot/espn/espn_bot.py`](../gamedaybot/espn/espn_bot.py) - **Main entry point**
- [`gamedaybot/espn/functionality.py`](../gamedaybot/espn/functionality.py) - **Core business logic**
- [`gamedaybot/espn/scheduler.py`](../gamedaybot/espn/scheduler.py) - **Automated scheduling**
- [`gamedaybot/chat/discord_bot.py`](../gamedaybot/chat/discord_bot.py) - **Interactive commands**

### Configuration Files
- [`requirements.txt`](../requirements.txt) - **Python dependencies**
- [`Dockerfile`](../Dockerfile) - **Container configuration**
- [`app.json`](../app.json) - **Heroku deployment config**
- [`.github/workflows/`](../.github/workflows/) - **CI/CD pipelines**

### Development Files
- [`tests/`](../tests/) - **Test suite**
- [`setup.py`](../setup.py) - **Package configuration**
- [`requirements-test.txt`](../requirements-test.txt) - **Test dependencies**

## 🎨 Code Style & Best Practices

### Python Style Guidelines
```python
# Follow PEP 8 style guide
# Use descriptive variable names
def get_weekly_scores(league, week=None):
    """
    Retrieve weekly scores with proper documentation.
    
    Args:
        league: ESPN League object
        week: Optional week number (defaults to current week)
        
    Returns:
        str: Formatted scores string
    """
    pass

# Use type hints where appropriate
from typing import Optional, List, Dict

def process_matchups(league: League, week: Optional[int] = None) -> str:
    pass
```

### Error Handling Patterns
```python
# Graceful error handling
try:
    scores = league.box_scores(week=week)
except Exception as e:
    logger.error(f"Failed to fetch scores: {e}")
    return "Unable to retrieve scores at this time"

# Validate inputs
def get_team_info(league, team_name: str) -> Optional[str]:
    if not team_name:
        return "Team name is required"
    
    # Process team lookup
    pass
```

### Logging Best Practices
```python
import logging

# Use module-level logger
logger = logging.getLogger(__name__)

# Log at appropriate levels
logger.debug("Fetching league data...")  # Development info
logger.info("Sending weekly scores")     # General info
logger.warning("ESPN API slow response") # Potential issues
logger.error("Failed to send message")   # Error conditions
```

## 🔧 Utility Functions

### Common Helper Functions ([`gamedaybot/utils/util.py`](../gamedaybot/utils/util.py))
```python
# String manipulation for chat platforms
def str_limit_check(text: str, limit: int) -> List[str]:
    """Split long messages for platform limits"""
    
def str_to_bool(value: str) -> bool:
    """Convert string environment variables to boolean"""
```

### ESPN Data Processing Patterns
```python
# Standard box score processing
def process_box_scores(league, week=None):
    box_scores = league.box_scores(week=week)
    results = []
    
    for matchup in box_scores:
        if matchup.away_team:  # Ensure valid matchup
            # Process home/away teams
            home_info = process_team_data(matchup.home_team, matchup.home_score)
            away_info = process_team_data(matchup.away_team, matchup.away_score)
            results.append(format_matchup(home_info, away_info))
    
    return results

# Player data processing
def process_lineup(lineup):
    starters = [p for p in lineup if p.slot_position not in ['BE', 'IR']]
    return sorted(starters, key=lambda p: p.slot_position)
```

## 🚀 Testing & Validation

### Manual Testing Checklist
- [ ] ESPN API connection works
- [ ] Chat platform webhooks respond
- [ ] Scheduled messages format correctly
- [ ] Discord commands execute properly
- [ ] Error handling works gracefully
- [ ] Timezone handling is correct

### Integration Testing
```python
# Use the dry run script for comprehensive testing
python tests/dry_run_all_functions.py

# Test specific ESPN functions
from gamedaybot.espn.functionality import get_scoreboard_short
from espn_api.football import League

league = League(league_id=123456, year=2024)
result = get_scoreboard_short(league)
print(result)
```

## 📝 Documentation Standards

### Function Documentation
```python
def get_power_rankings(league, week=None):
    """
    Calculate and format power rankings for the league.
    
    Power rankings are calculated using 2-step dominance algorithm
    weighted 80/15/5 for dominance/points/margin of victory.
    
    Parameters
    ----------
    league : espn_api.football.League
        ESPN League object with team and scoring data
    week : int, optional
        Week number for rankings (default: previous week)
        
    Returns
    -------
    str
        Formatted power rankings with change indicators
        
    Notes
    -----
    Rankings are normalized to 0-99.99 scale for display.
    Change indicators show movement from previous week.
    """
```

### Commit Message Guidelines
```bash
# Use descriptive commit messages
git commit -m "Add weekly MVP functionality with Discord command"
git commit -m "Fix timezone handling in scheduler for DST transitions" 
git commit -m "Update ESPN API integration for 2024 season changes"

# Use conventional commits for releases
git commit -m "feat: add player injury status tracking"
git commit -m "fix: handle empty lineup slots in optimal score calculation"
git commit -m "docs: update environment variable documentation"
```

This development guide provides everything needed to effectively work with and extend the fantasy football chat bot codebase.