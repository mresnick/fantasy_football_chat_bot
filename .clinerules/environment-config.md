# Fantasy Football Chat Bot - Environment & Configuration Guide

## 🔧 Environment Variables

### Required Variables

#### **Core ESPN Configuration**
```bash
# ESPN League Information
LEAGUE_ID=123456                    # Your ESPN League ID (required)
LEAGUE_YEAR=2024                    # Fantasy season year (required)
START_DATE=2024-09-03               # Season start date (YYYY-MM-DD)
END_DATE=2025-01-07                 # Season end date (YYYY-MM-DD)
TIMEZONE=America/New_York           # Local timezone for scheduling
```

#### **Chat Platform Configuration** 
*At least one chat platform is required:*

```bash
# GroupMe Integration
BOT_ID=your_groupme_bot_id          # GroupMe bot ID from dev.groupme.com

# Slack Integration  
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...  # Slack webhook URL

# Discord Integration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/... # Discord webhook URL

# Discord Bot (Interactive Commands)
DISCORD_TOKEN=your_discord_bot_token     # Discord bot token (optional)
DISCORD_SERVER_ID=123456789012345678     # Discord server ID (optional)
```

### Optional Variables

#### **Private League Access**
*Required for private ESPN leagues:*

```bash
ESPN_S2=your_espn_s2_cookie_value   # ESPN session cookie
SWID=your_swid_value               # ESPN user identifier (with or without {})
```

#### **Feature Flags**
```bash
TOP_HALF_SCORING=false             # Enable top-half scoring wins
RANDOM_PHRASE=false                # Add random phrases to matchups
MONITOR_REPORT=true                # Enable player injury monitoring
WAIVER_REPORT=true                 # Enable waiver wire reports
DAILY_WAIVER=false                 # Enable daily waiver reports
```

#### **Custom Messages**
```bash
INIT_MSG=Fantasy Football Bot is ready!  # Bot startup message
BROADCAST_MESSAGE=Custom announcement    # One-time broadcast message
```

## 🎯 Getting Configuration Values

### Finding Your ESPN League ID

#### Method 1: ESPN League URL
1. Go to your ESPN Fantasy Football league
2. Look at the URL: `https://fantasy.espn.com/football/league?leagueId=123456`
3. The `leagueId` parameter is your LEAGUE_ID

#### Method 2: ESPN Mobile App
1. Open ESPN Fantasy app
2. Go to your league
3. Tap "League" → "Settings"
4. League ID is displayed at the top

### Setting Up Chat Platform Integrations

#### GroupMe Setup

1. **Create GroupMe Bot:**
   ```
   1. Go to https://dev.groupme.com/session/new
   2. Click "Create Bot"
   3. Fill in bot details:
      - Bot Name: Fantasy Football Bot
      - Group: Your league chat
      - Avatar URL: (optional)
      - Callback URL: (leave blank)
   4. Copy the "Bot ID" for BOT_ID variable
   ```

2. **Test GroupMe Bot:**
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"bot_id":"YOUR_BOT_ID","text":"Test message"}' \
     https://api.groupme.com/v3/bots/post
   ```

#### Slack Setup

1. **Create Slack App:**
   ```
   1. Go to https://api.slack.com/apps/new
   2. Choose "From scratch"
   3. Name your app: "Fantasy Football Bot"
   4. Select your workspace
   ```

2. **Configure Incoming Webhook:**
   ```
   1. Go to "Incoming Webhooks" in your app settings
   2. Toggle "Activate Incoming Webhooks" to On
   3. Click "Add New Webhook to Workspace"
   4. Select the channel for messages
   5. Copy the webhook URL for SLACK_WEBHOOK_URL
   ```

3. **Test Slack Webhook:**
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"text":"Test message"}' \
     YOUR_SLACK_WEBHOOK_URL
   ```

#### Discord Setup

1. **Create Discord Webhook:**
   ```
   1. Go to your Discord server
   2. Right-click on the target channel
   3. Select "Edit Channel" → "Integrations"
   4. Click "Create Webhook"
   5. Name: "Fantasy Football Bot"
   6. Copy webhook URL for DISCORD_WEBHOOK_URL
   ```

2. **Create Discord Bot (Optional - for slash commands):**
   ```
   1. Go to https://discord.com/developers/applications
   2. Click "New Application"
   3. Name: "Fantasy Football Bot"
   4. Go to "Bot" section
   5. Click "Add Bot"
   6. Copy token for DISCORD_TOKEN
   7. Go to your server settings → "Roles"
   8. Copy server ID for DISCORD_SERVER_ID
   ```

3. **Test Discord Webhook:**
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"content":"Test message"}' \
     YOUR_DISCORD_WEBHOOK_URL
   ```

### Private League Credentials

#### Finding ESPN_S2 and SWID

1. **Using Browser Developer Tools:**
   ```
   1. Log into ESPN Fantasy Football
   2. Open Developer Tools (F12)
   3. Go to Application/Storage → Cookies → fantasy.espn.com
   4. Find 'espn_s2' cookie value → copy for ESPN_S2
   5. Find 'SWID' cookie value → copy for SWID
   ```

2. **Alternative Method (Chrome):**
   ```
   1. Log into ESPN Fantasy
   2. Right-click → "Inspect"
   3. Application tab → Cookies → fantasy.espn.com
   4. Look for espn_s2 and SWID entries
   ```

3. **SWID Format:**
   ```bash
   # SWID can be with or without curly braces
   SWID={ABC123-DEF456-GHI789}     # With braces
   SWID=ABC123-DEF456-GHI789       # Without braces (bot will add them)
   ```

## 🌐 Environment-Specific Configuration

### Local Development

#### Using .env File
Create `.env` file in project root:
```bash
# Core Configuration
LEAGUE_ID=123456
LEAGUE_YEAR=2024
START_DATE=2024-09-03  
END_DATE=2025-01-07
TIMEZONE=America/New_York

# Chat Platforms (use test values for development)
BOT_ID=test_bot_id
SLACK_WEBHOOK_URL=https://httpbin.org/post  # Test endpoint
DISCORD_WEBHOOK_URL=https://httpbin.org/post

# Private League (if needed)
ESPN_S2=your_espn_s2_value
SWID=your_swid_value

# Feature Flags
TOP_HALF_SCORING=false
RANDOM_PHRASE=true
MONITOR_REPORT=true
WAIVER_REPORT=true

# Development Messages
INIT_MSG=Fantasy Bot [DEV] is ready!
```

#### Loading Environment Variables
```python
# For local development
from dotenv import load_dotenv
load_dotenv()

# Verify variables loaded
import os
print(f"League ID: {os.environ.get('LEAGUE_ID')}")
print(f"League Year: {os.environ.get('LEAGUE_YEAR')}")
```

### Production Deployment

#### Heroku Configuration
```bash
# Set all required variables
heroku config:set LEAGUE_ID=123456 \
  LEAGUE_YEAR=2024 \
  START_DATE=2024-09-03 \
  END_DATE=2025-01-07 \
  TIMEZONE=America/New_York \
  BOT_ID=your_groupme_bot_id \
  SLACK_WEBHOOK_URL=your_slack_webhook \
  DISCORD_WEBHOOK_URL=your_discord_webhook

# Set optional variables
heroku config:set ESPN_S2=your_espn_s2 \
  SWID=your_swid \
  TOP_HALF_SCORING=false \
  MONITOR_REPORT=true \
  WAIVER_REPORT=true \
  INIT_MSG="Fantasy Football Bot is ready!"

# View all config vars
heroku config

# Update single variable
heroku config:set LEAGUE_YEAR=2025
```

#### Docker Environment
```bash
# Using environment file
docker run --env-file .env fantasy-football-bot

# Using individual variables
docker run \
  -e LEAGUE_ID=123456 \
  -e LEAGUE_YEAR=2024 \
  -e BOT_ID=your_bot_id \
  -e TIMEZONE=America/New_York \
  fantasy-football-bot
```

## ⏰ Timezone Configuration

### Supported Timezones
```bash
# Common US Timezones
TIMEZONE=America/New_York          # Eastern Time
TIMEZONE=America/Chicago           # Central Time  
TIMEZONE=America/Denver            # Mountain Time
TIMEZONE=America/Los_Angeles       # Pacific Time

# Other Examples
TIMEZONE=Europe/London             # GMT/BST
TIMEZONE=Australia/Sydney          # AEDT/AEST
TIMEZONE=Asia/Tokyo               # JST
```

### Timezone Impact
- **Scheduled Messages**: All cron jobs use your specified timezone
- **Game Times**: ESPN provides times in Eastern, scheduler adjusts accordingly
- **DST Handling**: APScheduler automatically handles daylight saving changes

## 📅 Season Date Configuration

### Setting Start and End Dates

#### NFL Season Calendar (2024 Example)
```bash
# Pre-season: August
# Week 1: September 5-9, 2024
# Week 18: January 5-6, 2025
# Wild Card: January 13-15, 2025
# Championship: February 9, 2025

# Recommended dates:
START_DATE=2024-09-03  # Tuesday before Week 1
END_DATE=2025-01-14    # Tuesday after Wild Card weekend
```

#### Season Date Impact
- **Scheduler Activation**: Bot only runs scheduled jobs between these dates
- **Manual Commands**: Discord slash commands work year-round
- **Init Messages**: Sent when bot starts within season dates

## 🎛️ Feature Flag Configuration

### TOP_HALF_SCORING
```bash
TOP_HALF_SCORING=true   # Enable additional win for top half scoring
TOP_HALF_SCORING=false  # Standard ESPN scoring only (default)
```
- **Impact**: Adds extra win for teams in top half of weekly scoring
- **Display**: Shows (+X) next to team records in standings
- **Note**: ESPN now has this feature built-in, use sparingly

### MONITOR_REPORT
```bash
MONITOR_REPORT=true     # Enable player injury/status monitoring (default)
MONITOR_REPORT=false    # Disable monitoring reports
```
- **Schedule**: Sunday 7:30 AM, Thursday 7:30 AM, Monday 7:30 AM
- **Content**: Lists players with injury status (Q, D, O) in starting lineups
- **Value**: Helps managers make last-minute lineup decisions

### WAIVER_REPORT
```bash
WAIVER_REPORT=true      # Enable waiver wire transaction reports (default)
WAIVER_REPORT=false     # Disable waiver reports
```
- **Requirements**: Requires ESPN_S2 and SWID for private leagues
- **Schedule**: Wednesday 7:31 AM (after waivers process)
- **Content**: Shows adds, drops, and FAAB spending

## 🔍 Configuration Validation

### Environment Variable Checker
```python
# gamedaybot/espn/env_vars.py provides validation
from gamedaybot.espn.env_vars import get_env_vars

def validate_config():
    """Validate environment configuration"""
    try:
        config = get_env_vars()
        
        # Check required variables
        required = ['league_id', 'year', 'ff_start_date', 'ff_end_date', 'my_timezone']
        missing = [key for key in required if not config.get(key)]
        
        if missing:
            print(f"Missing required variables: {missing}")
            return False
            
        # Check at least one chat platform
        platforms = ['bot_id', 'slack_webhook_url', 'discord_webhook_url']
        if not any(len(str(config.get(p, ''))) > 1 for p in platforms):
            print("No chat platform configured")
            return False
            
        # Validate ESPN connection
        from espn_api.football import League
        league = League(league_id=config['league_id'], year=config['year'])
        print(f"✓ Connected to league: {league.settings.name}")
        
        return True
        
    except Exception as e:
        print(f"Configuration error: {e}")
        return False

# Run validation
if __name__ == "__main__":
    validate_config()
```

## 🚨 Troubleshooting Configuration Issues

### Common Issues

#### 1. ESPN Connection Failures
```python
# Issue: "League not found" or authentication errors
# Solutions:
# - Verify LEAGUE_ID is correct
# - For private leagues, ensure ESPN_S2 and SWID are valid
# - Check if league year matches LEAGUE_YEAR

# Test ESPN connection
from espn_api.football import League
import os

league_id = os.environ['LEAGUE_ID']
year = int(os.environ['LEAGUE_YEAR'])

try:
    # Try public league first
    league = League(league_id=league_id, year=year)
    print(f"Public league access: {league.settings.name}")
except:
    # Try with private league credentials
    espn_s2 = os.environ.get('ESPN_S2')
    swid = os.environ.get('SWID')
    if espn_s2 and swid:
        league = League(league_id=league_id, year=year, 
                       espn_s2=espn_s2, swid=swid)
        print(f"Private league access: {league.settings.name}")
    else:
        print("No valid credentials found")
```

#### 2. Chat Platform Issues
```python
# Issue: Messages not sending to chat platforms
# Debug each platform:

import requests

# Test GroupMe
def test_groupme(bot_id):
    if bot_id and bot_id != "1":
        response = requests.post(
            "https://api.groupme.com/v3/bots/post",
            json={"bot_id": bot_id, "text": "Test message"}
        )
        print(f"GroupMe: {response.status_code} - {response.text}")

# Test Slack  
def test_slack(webhook_url):
    if webhook_url and webhook_url != "1":
        response = requests.post(webhook_url, json={"text": "Test message"})
        print(f"Slack: {response.status_code} - {response.text}")

# Test Discord
def test_discord(webhook_url):
    if webhook_url and webhook_url != "1":
        response = requests.post(webhook_url, json={"content": "Test message"})
        print(f"Discord: {response.status_code} - {response.text}")
```

#### 3. Scheduler Not Running
```bash
# Issue: No automated messages being sent
# Debug steps:

# 1. Check if within season dates
python3 -c "
from datetime import datetime
import os
start = datetime.strptime(os.environ['START_DATE'], '%Y-%m-%d')
end = datetime.strptime(os.environ['END_DATE'], '%Y-%m-%d')
now = datetime.now()
print(f'Season: {start} to {end}')
print(f'Now: {now}')
print(f'In season: {start <= now <= end}')
"

# 2. Check environment variables
env | grep -E "(LEAGUE_|BOT_|SLACK_|DISCORD_|START_|END_|TIMEZONE)"

# 3. Test scheduler jobs manually
python3 -c "from gamedaybot.espn.espn_bot import espn_bot; espn_bot('init')"
```

### Configuration Best Practices

1. **Security**: Never commit real credentials to version control
2. **Testing**: Use test/dummy values for development
3. **Validation**: Always validate configuration before deployment
4. **Documentation**: Document any custom configuration for your league
5. **Backup**: Keep a secure backup of your configuration values
6. **Rotation**: Periodically rotate ESPN_S2/SWID cookies if they expire

This comprehensive configuration guide ensures proper setup and troubleshooting of the fantasy football chat bot across all deployment scenarios.