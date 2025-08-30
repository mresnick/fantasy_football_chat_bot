# Fantasy Football Chat Bot - File Structure Guide

## 📁 Project Organization

This document provides a comprehensive overview of the project's file structure and the purpose of each directory and key file.

```
fantasy_football_chat_bot/
├── .clinerules/                     # AI Assistant Documentation
│   ├── README.md                   # Documentation overview and quick start
│   ├── project-overview.md         # High-level project description
│   ├── architecture.md             # Technical architecture details
│   ├── development-guide.md        # Development setup and workflows
│   ├── deployment.md               # Deployment processes and CI/CD
│   ├── testing.md                  # Testing strategies and guidelines
│   ├── environment-config.md       # Environment variables and configuration
│   └── file-structure.md          # This file - project structure guide
├── .github/                        # GitHub Actions CI/CD workflows
│   └── workflows/
│       ├── docker-publish.yml     # Docker build and publish workflow
│       └── publish_image.yaml     # Alternative image publish workflow
├── gamedaybot/                     # Main Python package
│   ├── __init__.py
│   ├── chat/                       # Chat platform integrations
│   │   ├── __init__.py
│   │   ├── discord_bot.py          # Discord slash commands (interactive)
│   │   ├── discord.py              # Discord webhook integration
│   │   ├── groupme.py              # GroupMe API integration
│   │   └── slack.py                # Slack webhook integration
│   ├── espn/                       # ESPN Fantasy Football integration
│   │   ├── __init__.py
│   │   ├── env_vars.py             # Environment variable management
│   │   ├── espn_bot.py             # Main bot orchestrator and entry point
│   │   ├── functionality.py        # Core ESPN functionality and calculations
│   │   ├── scheduler.py            # APScheduler configuration and jobs
│   │   └── season_recap.py         # End-of-season analytics and reporting
│   └── utils/                      # Utility functions and helpers
│       ├── __init__.py
│       └── util.py                 # Common utility functions
├── tests/                          # Test suite
│   ├── conftest.py                 # Pytest fixtures and configuration
│   ├── dry_run_all_functions.py    # Manual integration test runner
│   ├── test_discord.py             # Discord integration tests
│   ├── test_groupme.py             # GroupMe integration tests
│   ├── test_slack.py               # Slack integration tests
│   └── test_utils.py               # Utility function tests
├── .gitignore                      # Git ignore patterns
├── app.json                        # Heroku deployment configuration
├── docker-compose.template.yml     # Docker Compose template
├── docker-compose.yml              # Docker Compose configuration
├── Dockerfile                      # Docker container definition
├── LICENSE                         # Project license (MIT)
├── Procfile                        # Heroku process definition
├── README.md                       # Main project documentation
├── requirements.txt                # Python dependencies
├── requirements-test.txt           # Test dependencies
├── runtime.txt                     # Python runtime version for Heroku
├── setup.cfg                       # Package configuration
└── setup.py                        # Package setup script
```

## 🎯 Core Directories

### `/gamedaybot/` - Main Application Package

The heart of the fantasy football chat bot, organized into logical modules:

#### **`/gamedaybot/espn/`** - ESPN Integration
- **Primary Purpose**: Interface with ESPN Fantasy Football API and process league data
- **Key Files**:
  - [`espn_bot.py`](../gamedaybot/espn/espn_bot.py) - **Main entry point** and orchestrator
  - [`functionality.py`](../gamedaybot/espn/functionality.py) - **Core business logic** for ESPN data processing
  - [`scheduler.py`](../gamedaybot/espn/scheduler.py) - **Automated scheduling** using APScheduler
  - [`env_vars.py`](../gamedaybot/espn/env_vars.py) - **Environment variable management**
  - [`season_recap.py`](../gamedaybot/espn/season_recap.py) - **Advanced analytics** for season summaries

#### **`/gamedaybot/chat/`** - Chat Platform Integrations
- **Primary Purpose**: Handle message delivery across multiple chat platforms
- **Key Files**:
  - [`groupme.py`](../gamedaybot/chat/groupme.py) - GroupMe webhook API integration
  - [`slack.py`](../gamedaybot/chat/slack.py) - Slack webhook API integration
  - [`discord.py`](../gamedaybot/chat/discord.py) - Discord webhook integration
  - [`discord_bot.py`](../gamedaybot/chat/discord_bot.py) - **Interactive Discord commands** using slash commands

#### **`/gamedaybot/utils/`** - Utility Functions
- **Primary Purpose**: Common helper functions and utilities
- **Key Files**:
  - [`util.py`](../gamedaybot/utils/util.py) - String manipulation, boolean conversion, message splitting

### `/tests/` - Test Suite

Comprehensive testing infrastructure for all components:

- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Component interaction validation
- **Mock Tests**: External API simulation
- **Manual Tests**: [`dry_run_all_functions.py`](../tests/dry_run_all_functions.py) for real-world validation

### `/.github/workflows/` - CI/CD Pipeline

GitHub Actions workflows for automated testing and deployment:

- **[`docker-publish.yml`](../.github/workflows/docker-publish.yml)**: Builds and publishes Docker images
- **Continuous Integration**: Runs tests across multiple Python versions
- **Container Registry**: Publishes to GitHub Container Registry (ghcr.io)

### `/.clinerules/` - AI Assistant Documentation

Comprehensive documentation to help AI assistants understand and work with the codebase:

- **Architecture guides**: Technical system design
- **Development workflows**: Setup and best practices  
- **Deployment processes**: Multiple deployment options
- **Configuration management**: Environment variables and setup

## 📄 Key Configuration Files

### **Application Configuration**

#### [`app.json`](../app.json)
```json
{
  "name": "ESPN Fantasy Football Chat Bot",
  "description": "Fantasy football bot for GroupMe, Slack, and Discord",
  "env": {
    "LEAGUE_ID": {"description": "ESPN League ID", "required": true},
    "LEAGUE_YEAR": {"description": "ESPN League Year", "value": "2024"}
  }
}
```
- **Purpose**: Heroku one-click deployment configuration
- **Contains**: App metadata, required environment variables, add-on specifications

#### [`Procfile`](../Procfile)
```
worker: python gamedaybot/espn/espn_bot.py
```
- **Purpose**: Defines how Heroku runs the application
- **Type**: Worker process (background/scheduled execution)

#### [`runtime.txt`](../runtime.txt)
```
python-3.9.x
```
- **Purpose**: Specifies Python version for Heroku deployment

### **Docker Configuration**

#### [`Dockerfile`](../Dockerfile)
- **Purpose**: Defines containerized application environment
- **Base Image**: Python official image
- **Process**: Installs dependencies, copies code, sets entrypoint

#### [`docker-compose.yml`](../docker-compose.yml) / [`docker-compose.template.yml`](../docker-compose.template.yml)
- **Purpose**: Local development and multi-container deployment
- **Template**: Provides example configuration with environment variable placeholders

### **Python Configuration**

#### [`requirements.txt`](../requirements.txt)
```
flake8==3.3.0
apscheduler>=3.3.0,<4.0.0
requests>=2.0.0,<3.0.0
espn_api>=0.43.0
datetime
discord>=2.3.2
```
- **Purpose**: Production dependencies
- **Key Packages**: ESPN API, APScheduler, Discord.py, Requests

#### [`requirements-test.txt`](../requirements-test.txt)
- **Purpose**: Additional dependencies for testing
- **Includes**: pytest, requests-mock, coverage tools

#### [`setup.py`](../setup.py)
```python
setup(
    name='gamedaybot',
    version='0.3.1',
    description='ESPN fantasy football Chat Bot',
    install_requires=['espn_api>=0.43.0', 'requests>=2.0.0,<3.0.0', ...]
)
```
- **Purpose**: Package installation and metadata
- **Usage**: `pip install -e .` for development installation

## 🔍 File Navigation Guide

### **Making Code Changes**

#### Adding New ESPN Functionality
1. **Core Logic**: Add functions to [`gamedaybot/espn/functionality.py`](../gamedaybot/espn/functionality.py)
2. **Bot Integration**: Register in [`gamedaybot/espn/espn_bot.py`](../gamedaybot/espn/espn_bot.py)
3. **Scheduling**: Add to [`gamedaybot/espn/scheduler.py`](../gamedaybot/espn/scheduler.py) if automated
4. **Discord Commands**: Extend [`gamedaybot/chat/discord_bot.py`](../gamedaybot/chat/discord_bot.py) if interactive
5. **Testing**: Add tests in [`tests/`](../tests/) directory

#### Modifying Chat Integrations
- **GroupMe**: [`gamedaybot/chat/groupme.py`](../gamedaybot/chat/groupme.py)
- **Slack**: [`gamedaybot/chat/slack.py`](../gamedaybot/chat/slack.py)
- **Discord Webhooks**: [`gamedaybot/chat/discord.py`](../gamedaybot/chat/discord.py)
- **Discord Commands**: [`gamedaybot/chat/discord_bot.py`](../gamedaybot/chat/discord_bot.py)

#### Configuration Changes
- **Environment Variables**: [`gamedaybot/espn/env_vars.py`](../gamedaybot/espn/env_vars.py)
- **Deployment Settings**: [`app.json`](../app.json), [`Dockerfile`](../Dockerfile)
- **Dependencies**: [`requirements.txt`](../requirements.txt)

### **Understanding Data Flow**

#### Message Flow Path
```
Scheduler → ESPN Bot → Functionality → ESPN API
                   ↓
Chat Platforms ← ESPN Bot ← Formatted Message
```

#### Key Entry Points
1. **Scheduled Execution**: [`gamedaybot/espn/scheduler.py`](../gamedaybot/espn/scheduler.py) → [`espn_bot.py`](../gamedaybot/espn/espn_bot.py)
2. **Manual Execution**: Direct call to [`espn_bot.py`](../gamedaybot/espn/espn_bot.py) functions
3. **Discord Commands**: [`discord_bot.py`](../gamedaybot/chat/discord_bot.py) → [`functionality.py`](../gamedaybot/espn/functionality.py)

## 🚀 Quick Reference

### **Most Frequently Modified Files**
1. **[`gamedaybot/espn/functionality.py`](../gamedaybot/espn/functionality.py)** - Adding new ESPN features
2. **[`gamedaybot/espn/scheduler.py`](../gamedaybot/espn/scheduler.py)** - Modifying message schedules  
3. **[`gamedaybot/chat/discord_bot.py`](../gamedaybot/chat/discord_bot.py)** - Adding Discord commands
4. **[`requirements.txt`](../requirements.txt)** - Managing dependencies
5. **[`app.json`](../app.json)** - Deployment configuration

### **Configuration Files by Environment**
- **Development**: `.env`, `docker-compose.yml`
- **Production**: Heroku config vars, environment variables
- **Testing**: `requirements-test.txt`, `conftest.py`
- **CI/CD**: `.github/workflows/`, Docker configurations

This file structure guide provides comprehensive understanding of how the fantasy football chat bot project is organized, making it easier to navigate, modify, and extend the codebase effectively.