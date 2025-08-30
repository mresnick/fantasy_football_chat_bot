# Fantasy Football Chat Bot - Testing Guide

## 🧪 Testing Strategy

### Testing Philosophy
This project uses a comprehensive testing approach that covers:
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Full workflow validation
- **Mock Testing**: External API simulation
- **Manual Testing**: Human verification of bot behavior

### Test Structure Overview
```
tests/
├── conftest.py              # Pytest fixtures and shared configuration
├── test_discord.py          # Discord integration tests
├── test_groupme.py          # GroupMe integration tests
├── test_slack.py            # Slack integration tests
├── test_utils.py            # Utility function tests
└── dry_run_all_functions.py # Manual integration test runner
```

## 🛠️ Testing Framework & Tools

### Core Testing Stack
- **pytest**: Primary testing framework
- **requests-mock**: HTTP request mocking
- **pytest-cov**: Code coverage reporting
- **unittest.mock**: Python standard library mocking

### Installation
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Key packages installed:
# - pytest>=6.0.0
# - pytest-cov>=2.0.0
# - requests-mock>=1.8.0
# - mock>=4.0.0
```

## 📋 Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_functionality.py

# Run specific test function
pytest tests/test_groupme.py::test_send_message

# Run tests matching pattern
pytest -k "test_scoreboard"
```

### Coverage Testing
```bash
# Run tests with coverage
pytest --cov=gamedaybot

# Generate HTML coverage report
pytest --cov=gamedaybot --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=gamedaybot --cov-report=xml

# Show missing lines
pytest --cov=gamedaybot --cov-report=term-missing
```

### Parallel Testing
```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

## 🎯 Test Categories

### 1. Unit Tests

#### ESPN Functionality Tests
```python
# tests/test_functionality.py
import pytest
from unittest.mock import Mock, patch
from gamedaybot.espn.functionality import get_scoreboard_short

def test_get_scoreboard_short():
    """Test scoreboard formatting"""
    # Create mock league and box scores
    mock_league = Mock()
    mock_box_score = Mock()
    mock_box_score.home_team.team_abbrev = "TEAM1"
    mock_box_score.away_team.team_abbrev = "TEAM2"
    mock_box_score.home_score = 123.45
    mock_box_score.away_score = 67.89
    mock_box_score.away_team = True  # Ensure away team exists
    
    mock_league.box_scores.return_value = [mock_box_score]
    
    result = get_scoreboard_short(mock_league)
    
    assert "Score Update" in result
    assert "TEAM1" in result
    assert "TEAM2" in result
    assert "123.45" in result
    assert "67.89" in result

def test_get_standings():
    """Test standings calculation"""
    mock_league = Mock()
    mock_team1 = Mock()
    mock_team1.team_name = "Team One"
    mock_team1.wins = 5
    mock_team1.losses = 2
    
    mock_team2 = Mock()
    mock_team2.team_name = "Team Two"
    mock_team2.wins = 3
    mock_team2.losses = 4
    
    mock_league.standings.return_value = [mock_team1, mock_team2]
    
    from gamedaybot.espn.functionality import get_standings
    result = get_standings(mock_league)
    
    assert "Current Standings" in result
    assert "Team One" in result
    assert "(5-2)" in result
    assert "Team Two" in result
    assert "(3-4)" in result
```

### 2. Chat Platform Tests

#### GroupMe Integration Tests
```python
# tests/test_groupme.py
import pytest
import requests_mock
from gamedaybot.chat.groupme import GroupMe, GroupMeException

def test_groupme_send_message_success(mock_requests):
    """Test successful GroupMe message sending"""
    bot_id = "test_bot_id"
    message = "Test message"
    
    mock_requests.post(
        "https://api.groupme.com/v3/bots/post",
        status_code=202
    )
    
    groupme = GroupMe(bot_id)
    response = groupme.send_message(message)
    
    assert response.status_code == 202
    assert mock_requests.call_count == 1
    
    # Verify request payload
    request = mock_requests.request_history[0]
    assert request.json()["bot_id"] == bot_id
    assert request.json()["text"] == message

def test_groupme_send_message_failure(mock_requests):
    """Test GroupMe message sending failure"""
    mock_requests.post(
        "https://api.groupme.com/v3/bots/post",
        status_code=400,
        text="Bad Request"
    )
    
    groupme = GroupMe("test_bot_id")
    
    with pytest.raises(GroupMeException):
        groupme.send_message("Test message")
```

### 3. Integration Tests

#### End-to-End ESPN Bot Tests
```python
# tests/test_espn_bot_integration.py
import pytest
from unittest.mock import Mock, patch
from gamedaybot.espn.espn_bot import espn_bot

@patch('gamedaybot.espn.espn_bot.get_env_vars')
@patch('gamedaybot.chat.groupme.GroupMe')
@patch('gamedaybot.chat.slack.Slack')
@patch('gamedaybot.chat.discord.Discord')
@patch('espn_api.football.League')
def test_espn_bot_get_scoreboard(mock_league, mock_discord, mock_slack, mock_groupme, mock_env):
    """Test full ESPN bot scoreboard workflow"""
    # Configure mocks
    mock_env.return_value = {
        'league_id': '123456',
        'year': 2024,
        'bot_id': 'test_bot',
        'slack_webhook_url': 'test_url',
        'discord_webhook_url': 'test_url',
        'str_limit': 2000
    }
    
    mock_league_instance = Mock()
    mock_league.return_value = mock_league_instance
    
    # Mock chat platform instances
    mock_groupme_instance = Mock()
    mock_slack_instance = Mock()
    mock_discord_instance = Mock()
    
    mock_groupme.return_value = mock_groupme_instance
    mock_slack.return_value = mock_slack_instance
    mock_discord.return_value = mock_discord_instance
    
    # Mock functionality
    with patch('gamedaybot.espn.functionality.get_scoreboard_short') as mock_scoreboard:
        mock_scoreboard.return_value = "Test Scoreboard Data"
        
        # Execute bot function
        espn_bot('get_scoreboard_short')
        
        # Verify all platforms were called
        mock_groupme_instance.send_message.assert_called_once_with("Test Scoreboard Data")
        mock_slack_instance.send_message.assert_called_once_with("Test Scoreboard Data")
        mock_discord_instance.send_message.assert_called_once_with("Test Scoreboard Data")
```

## 🔧 Mock Testing Patterns

### ESPN API Mocking
```python
# Common mock patterns for ESPN API objects

def create_mock_league():
    """Create a mock ESPN League object"""
    mock_league = Mock()
    mock_league.league_id = 123456
    mock_league.year = 2024
    mock_league.current_week = 5
    mock_league.settings.name = "Test League"
    return mock_league

def create_mock_team(name="Test Team", abbrev="TEST", wins=3, losses=2):
    """Create a mock ESPN Team object"""
    mock_team = Mock()
    mock_team.team_name = name
    mock_team.team_abbrev = abbrev
    mock_team.wins = wins
    mock_team.losses = losses
    mock_team.playoff_pct = 75.5
    return mock_team

def create_mock_box_score(home_team, away_team, home_score=100.0, away_score=95.0):
    """Create a mock ESPN BoxScore object"""
    mock_box_score = Mock()
    mock_box_score.home_team = home_team
    mock_box_score.away_team = away_team
    mock_box_score.home_score = home_score
    mock_box_score.away_score = away_score
    mock_box_score.home_projected = home_score + 5
    mock_box_score.away_projected = away_score + 3
    return mock_box_score
```

### HTTP Request Mocking
```python
# conftest.py - shared fixtures
import pytest
import requests_mock

@pytest.fixture
def mock_requests():
    """Provide a requests mocker for all tests"""
    with requests_mock.Mocker() as m:
        yield m

@pytest.fixture
def mock_groupme_api(mock_requests):
    """Mock GroupMe API responses"""
    mock_requests.post(
        "https://api.groupme.com/v3/bots/post",
        status_code=202
    )
    return mock_requests

@pytest.fixture
def mock_slack_webhook(mock_requests):
    """Mock Slack webhook responses"""
    mock_requests.post(
        requests_mock.ANY,
        text="ok"
    )
    return mock_requests
```

## 🏃‍♂️ Manual Testing

### Dry Run Testing
The project includes a comprehensive dry run script for manual testing:

```python
# tests/dry_run_all_functions.py

"""
Manual test runner for validating all ESPN bot functions
Usage: python tests/dry_run_all_functions.py
"""

from gamedaybot.espn.espn_bot import espn_bot
from gamedaybot.espn.functionality import *
from espn_api.football import League
import os

def test_all_functions():
    """Test all ESPN bot functions with real data"""
    
    # Load environment variables
    league_id = os.environ.get('LEAGUE_ID')
    year = int(os.environ.get('LEAGUE_YEAR', 2024))
    
    if not league_id:
        print("Please set LEAGUE_ID environment variable")
        return
    
    try:
        league = League(league_id=league_id, year=year)
        print(f"Connected to league: {league.settings.name}")
        
        # Test each function
        functions_to_test = [
            'get_scoreboard_short',
            'get_projected_scoreboard',
            'get_standings',
            'get_matchups',
            'get_power_rankings',
            'get_trophies',
            'get_monitor'
        ]
        
        for func_name in functions_to_test:
            print(f"\n--- Testing {func_name} ---")
            try:
                espn_bot(func_name)
                print("✓ SUCCESS")
            except Exception as e:
                print(f"✗ FAILED: {e}")
                
    except Exception as e:
        print(f"Failed to connect to league: {e}")

if __name__ == "__main__":
    test_all_functions()
```

### Manual Test Checklist
```bash
# 1. Environment Setup
export LEAGUE_ID=your_test_league_id
export LEAGUE_YEAR=2024
export BOT_ID=test  # Use test value to avoid sending real messages

# 2. Basic Function Tests
python -c "from gamedaybot.espn.espn_bot import espn_bot; espn_bot('get_scoreboard_short')"
python -c "from gamedaybot.espn.espn_bot import espn_bot; espn_bot('get_standings')"
python -c "from gamedaybot.espn.espn_bot import espn_bot; espn_bot('get_power_rankings')"

# 3. Discord Bot Tests (if enabled)
# Test slash commands manually in Discord

# 4. Error Handling Tests
export LEAGUE_ID=invalid_id
python -c "from gamedaybot.espn.espn_bot import espn_bot; espn_bot('get_scoreboard_short')"
```

## 📊 Test Coverage Goals

### Coverage Targets
- **Overall Coverage**: > 80%
- **Core Functionality**: > 90%
- **Chat Integrations**: > 85%
- **Error Handling**: > 75%

### Coverage Analysis
```bash
# Generate detailed coverage report
pytest --cov=gamedaybot --cov-report=html --cov-report=term-missing

# View coverage by module
pytest --cov=gamedaybot.espn --cov-report=term
pytest --cov=gamedaybot.chat --cov-report=term
pytest --cov=gamedaybot.utils --cov-report=term

# Find untested lines
pytest --cov=gamedaybot --cov-report=term-missing | grep "TOTAL"
```

### Coverage Configuration
```ini
# .coveragerc
[run]
source = gamedaybot
omit = 
    */tests/*
    */venv/*
    setup.py
    gamedaybot/espn/env_vars.py  # Environment-dependent

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

## 🚀 Continuous Integration Testing

### GitHub Actions Test Configuration
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, "3.10"]
        
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          
      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements-test.txt') }}
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
          
      - name: Run tests with pytest
        run: |
          pytest --cov=gamedaybot --cov-report=xml --cov-report=term-missing
          
      - name: Upload coverage to Codecov
        if: matrix.python-version == '3.9'
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
```

### Test Quality Gates
```bash
# Minimum coverage threshold
pytest --cov=gamedaybot --cov-fail-under=80

# Test performance benchmarking
pytest --benchmark-only

# Security testing with bandit
bandit -r gamedaybot/

# Code quality with flake8
flake8 gamedaybot/ tests/
```

This comprehensive testing guide ensures robust validation of the fantasy football chat bot across all components and deployment scenarios.