# Fantasy Football Chat Bot - Project Overview

## 📖 Project Description

This is a comprehensive Fantasy Football Chat Bot that integrates with ESPN Fantasy Football to provide automated league updates and interactive commands across multiple messaging platforms. The bot serves as a league commissioner's assistant, delivering timely and engaging content to keep league members informed and entertained throughout the fantasy football season.

## 🎯 Purpose & Goals

### Primary Purpose
- **Automate Fantasy Football Communication**: Reduce manual effort for league commissioners by automatically posting relevant league updates
- **Increase League Engagement**: Keep league members actively engaged with regular updates, statistics, and fun features
- **Multi-Platform Support**: Provide flexibility by supporting GroupMe, Slack, and Discord simultaneously

### Key Goals
- Deliver consistent, scheduled fantasy football content
- Provide real-time scoring updates during game days
- Offer interactive commands for on-demand information
- Support both automated messaging and user-triggered commands

## ⭐ Key Features

### Automated Scheduled Messages
- **Scoreboard Updates**: Current scores posted at strategic times (Friday/Monday mornings, Sunday afternoon/evening)
- **Weekly Matchups**: Thursday evening previews with team records and projections
- **Power Rankings**: Tuesday evening analysis using advanced algorithms
- **League Standings**: Wednesday morning standings with optional top-half scoring
- **Trophies**: Tuesday morning awards (highest/lowest scores, biggest blowout, closest win)
- **Waiver Reports**: Wednesday morning transaction summaries (requires ESPN_S2/SWID)
- **Close Scores**: Monday evening alerts for games within 15 points
- **Player Monitoring**: Sunday morning injury/status reports

### Interactive Discord Commands
- `/current_scores` - Get current week's scores
- `/scoreboard <week>` - Get scores for specific week
- `/projected_scores` - View projected scores
- `/standings` - Current league standings
- `/players_to_monitor` - Injury reports
- `/matchups` - Weekly matchups
- `/close_scores` - Close projected games
- `/power_rankings` - Power rankings
- `/lineup <team_name> [week]` - Team lineup details
- `/player_status <player_name>` - Player injury status
- `/cmc` - Christian McCaffrey injury status (easter egg)
- `/recap` - Season recap
- `/win_matrix` - Win/loss matrix analysis

### Advanced Analytics
- **Power Rankings**: 2-step dominance algorithm with points scored and margin of victory (80/15/5 weighting)
- **Optimal Lineup Analysis**: Compare actual vs optimal scores
- **Achievement Tracking**: Over/under achievers, lucky/unlucky teams
- **Activity Monitoring**: Most active vs laziest managers
- **Win Matrix**: Head-to-head record analysis
- **Season Recap**: Comprehensive end-of-season statistics

## 🏗️ Architecture Overview

### Core Components

1. **ESPN Integration** (`gamedaybot/espn/`)
   - `espn_bot.py` - Main bot orchestrator and entry point
   - `functionality.py` - Core ESPN API functionality and calculations
   - `scheduler.py` - Automated message scheduling
   - `env_vars.py` - Environment variable management
   - `season_recap.py` - End-of-season analytics

2. **Chat Platform Integrations** (`gamedaybot/chat/`)
   - `groupme.py` - GroupMe webhook integration
   - `slack.py` - Slack webhook integration
   - `discord.py` - Discord webhook integration
   - `discord_bot.py` - Discord slash commands (bot)

3. **Utilities** (`gamedaybot/utils/`)
   - `util.py` - Common utility functions

4. **Testing** (`tests/`)
   - Unit tests for all major components
   - Mock fixtures for external API calls

### Key Dependencies
- `espn_api>=0.43.0` - ESPN Fantasy Football API wrapper
- `apscheduler>=3.3.0` - Cron-like job scheduling
- `requests>=2.0.0` - HTTP requests for webhooks
- `discord>=2.3.2` - Discord bot functionality
- `pytest` - Testing framework

## 🔄 Workflow & Data Flow

### Scheduled Messages Flow
1. **Scheduler** (`scheduler.py`) triggers functions based on cron schedule
2. **ESPN Bot** (`espn_bot.py`) orchestrates the request
3. **Functionality** (`functionality.py`) fetches ESPN data and generates content
4. **Chat Adapters** format and send messages to all configured platforms

### Interactive Commands Flow
1. **Discord Bot** (`discord_bot.py`) receives slash command
2. **ESPN League** data is accessed directly
3. **Functionality** (`functionality.py`) processes request and formats response
4. **Discord** sends formatted response back to user

### Configuration Flow
1. **Environment Variables** are loaded via `env_vars.py`
2. **ESPN League** object is initialized with credentials
3. **Chat Platform** objects are initialized with webhooks/tokens
4. **Scheduler** sets up all automated jobs with proper timezones

## 🎨 Design Patterns

### Strategy Pattern
- Multiple chat platform implementations with common interface
- Flexible message delivery across GroupMe, Slack, Discord

### Template Method Pattern
- Consistent message formatting across different content types
- Reusable ESPN data processing workflows

### Factory Pattern
- League object creation with optional private league credentials
- Chat bot initialization based on available configuration

## 🚀 Deployment Options

### Heroku (Primary)
- One-click deployment with environment variable configuration
- Automatic scaling and process management
- Cost-effective for small-to-medium leagues

### Docker
- Containerized deployment for any Docker-compatible platform
- Consistent environment across development and production
- Easy scaling and management

### Local Development
- Direct Python execution for testing and development
- Full feature set available for local testing

## 🔧 Configuration Management

### Required Environment Variables
- `LEAGUE_ID` - ESPN League ID
- `LEAGUE_YEAR` - Fantasy season year
- `START_DATE` / `END_DATE` - Season date range
- `TIMEZONE` - Local timezone for scheduling
- Chat platform webhooks (BOT_ID, SLACK_WEBHOOK_URL, DISCORD_WEBHOOK_URL)

### Optional Features
- `ESPN_S2` / `SWID` - Private league access
- `TOP_HALF_SCORING` - Additional win criteria
- `MONITOR_REPORT` - Player injury monitoring
- `WAIVER_REPORT` - Transaction tracking
- `RANDOM_PHRASE` - Fun matchup additions

## 📊 Target Users

### Primary Users
- **Fantasy Football League Commissioners** - Seeking to automate league communication
- **League Members** - Wanting convenient access to league information

### Use Cases
- **Casual Leagues** - Friends/family leagues wanting basic automation
- **Competitive Leagues** - Advanced analytics and detailed reporting
- **Multiple Platform Leagues** - Members across different chat platforms
- **Private ESPN Leagues** - Leagues requiring authentication

## 🎯 Success Metrics

- **Engagement**: Increased participation in league chat channels
- **Automation**: Reduced manual effort for commissioners
- **Accuracy**: Reliable, timely delivery of ESPN data
- **Adoption**: Successful deployment across multiple platforms
- **User Satisfaction**: Positive feedback from league members