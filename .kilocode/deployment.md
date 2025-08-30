# Fantasy Football Chat Bot - Deployment Guide

## 🚀 Deployment Options

### 1. Heroku Deployment (Recommended)

#### One-Click Deployment
The easiest way to deploy the bot is using Heroku's one-click deployment:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

This will:
- Create a new Heroku app
- Set up the necessary environment variables
- Deploy the latest version from the repository
- Configure the worker dyno

#### Manual Heroku Setup

```bash
# Install Heroku CLI
# Create new app
heroku create your-fantasy-bot-name

# Set environment variables
heroku config:set LEAGUE_ID=123456
heroku config:set LEAGUE_YEAR=2024
heroku config:set BOT_ID=your_groupme_bot_id
heroku config:set START_DATE=2024-09-03
heroku config:set END_DATE=2025-01-07
heroku config:set TIMEZONE=America/New_York

# Deploy
git push heroku main

# Scale worker dyno
heroku ps:scale worker=1
```

#### Heroku Configuration Files

**[`app.json`](../app.json)** - One-click deployment configuration:
```json
{
  "name": "ESPN Fantasy Football Chat Bot",
  "description": "Fantasy football bot for GroupMe, Slack, and Discord",
  "repository": "https://github.com/dtcarls/fantasy_football_chat_bot",
  "keywords": ["python", "fantasy-football", "espn", "groupme", "slack", "discord"],
  "env": {
    "LEAGUE_ID": {
      "description": "ESPN League ID",
      "required": true
    },
    "LEAGUE_YEAR": {
      "description": "ESPN League Year",
      "value": "2024"
    }
  }
}
```

**[`Procfile`](../Procfile)** - Process definition:
```
worker: python gamedaybot/espn/espn_bot.py
```

**[`runtime.txt`](../runtime.txt)** - Python version:
```
python-3.9.x
```

### 2. Docker Deployment

#### Local Docker Build
```bash
# Build image
docker build -t fantasy-football-bot .

# Run with environment file
docker run --env-file .env fantasy-football-bot

# Run with individual environment variables
docker run \
  -e LEAGUE_ID=123456 \
  -e LEAGUE_YEAR=2024 \
  -e BOT_ID=your_bot_id \
  -e TIMEZONE=America/New_York \
  fantasy-football-bot
```

#### Docker Compose
Create a `docker-compose.yml`:
```yaml
version: '3.8'
services:
  fantasy-bot:
    build: .
    environment:
      - LEAGUE_ID=${LEAGUE_ID}
      - LEAGUE_YEAR=${LEAGUE_YEAR}
      - BOT_ID=${BOT_ID}
      - TIMEZONE=${TIMEZONE}
      - START_DATE=${START_DATE}
      - END_DATE=${END_DATE}
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

#### Pre-built Docker Images
Pull from GitHub Container Registry:
```bash
# Pull latest image
docker pull ghcr.io/dtcarls/fantasy_football_chat_bot:latest

# Run pre-built image
docker run --env-file .env ghcr.io/dtcarls/fantasy_football_chat_bot:latest
```

### 3. Cloud Platform Deployment

#### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy fantasy-football-bot \
  --image gcr.io/PROJECT_ID/fantasy-football-bot \
  --platform managed \
  --set-env-vars LEAGUE_ID=123456,BOT_ID=your_bot_id
```

#### AWS ECS/Fargate
```bash
# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Run task
aws ecs run-task --cluster your-cluster --task-definition fantasy-football-bot
```

#### Azure Container Instances
```bash
# Deploy to Azure
az container create \
  --resource-group myResourceGroup \
  --name fantasy-football-bot \
  --image ghcr.io/dtcarls/fantasy_football_chat_bot:latest \
  --environment-variables LEAGUE_ID=123456 BOT_ID=your_bot_id
```

### 4. VPS/Server Deployment

#### Systemd Service Setup
Create `/etc/systemd/system/fantasy-bot.service`:
```ini
[Unit]
Description=Fantasy Football Chat Bot
After=network.target

[Service]
Type=simple
User=fantasy-bot
WorkingDirectory=/opt/fantasy-football-bot
ExecStart=/opt/fantasy-football-bot/venv/bin/python gamedaybot/espn/espn_bot.py
Restart=always
RestartSec=10
Environment=LEAGUE_ID=123456
Environment=BOT_ID=your_bot_id
EnvironmentFile=/opt/fantasy-football-bot/.env

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fantasy-bot
sudo systemctl start fantasy-bot
sudo systemctl status fantasy-bot
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Docker Build and Publish ([`.github/workflows/docker-publish.yml`](../.github/workflows/docker-publish.yml))

**Triggers:**
- Push to `master` branch
- Pull requests to `master`
- Daily cron schedule
- Manual workflow dispatch
- Git tags (releases)

**Process:**
```yaml
name: Docker

on:
  push:
    branches: [ "master" ]
    tags: [ 'v*.*.*' ]
  pull_request:
    branches: [ "master" ]
  schedule:
    - cron: '37 4 * * *'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Log into registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Key Features:**
- **Multi-platform builds** (linux/amd64, linux/arm64)
- **GitHub Container Registry** (ghcr.io) publishing
- **Docker layer caching** for faster builds
- **Cosign signing** for image security
- **Automatic tagging** based on git refs

#### 2. Continuous Integration ([`.github/workflows/ci.yaml`](../.github/workflows/ci.yaml))

**Test Pipeline:**
```yaml
name: CI

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
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
          
      - name: Run tests with pytest
        run: |
          pytest --cov=gamedaybot --cov-report=xml
          
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
```

### Deployment Strategies

#### 1. Blue-Green Deployment (Heroku)
```bash
# Create staging app
heroku create your-bot-staging

# Deploy to staging
git push staging main

# Test staging environment
heroku run --app your-bot-staging "python -c 'from gamedaybot.espn.espn_bot import espn_bot; espn_bot(\"init\")'"

# Promote to production
heroku pipelines:promote --app your-bot-staging --to your-bot-production
```

#### 2. Rolling Updates (Docker)
```bash
# Update with zero-downtime
docker build -t fantasy-football-bot:v2 .
docker stop fantasy-bot-old || true
docker run -d --name fantasy-bot-new fantasy-football-bot:v2
docker rm fantasy-bot-old || true
docker rename fantasy-bot-new fantasy-bot
```

## 🔧 Configuration Management

### Environment Variable Deployment

#### Heroku Config Vars
```bash
# Set all required variables
heroku config:set \
  LEAGUE_ID=123456 \
  LEAGUE_YEAR=2024 \
  START_DATE=2024-09-03 \
  END_DATE=2025-01-07 \
  TIMEZONE=America/New_York \
  BOT_ID=your_groupme_bot_id \
  SLACK_WEBHOOK_URL=your_slack_webhook \
  DISCORD_WEBHOOK_URL=your_discord_webhook

# Optional features
heroku config:set \
  ESPN_S2=your_espn_s2_cookie \
  SWID=your_swid \
  TOP_HALF_SCORING=false \
  MONITOR_REPORT=true \
  WAIVER_REPORT=true \
  INIT_MSG="Fantasy Bot is ready!"
```

#### Docker Environment Files
Create `.env` file:
```bash
# Core Configuration
LEAGUE_ID=123456
LEAGUE_YEAR=2024
START_DATE=2024-09-03
END_DATE=2025-01-07
TIMEZONE=America/New_York

# Chat Platforms
BOT_ID=your_groupme_bot_id
SLACK_WEBHOOK_URL=your_slack_webhook
DISCORD_WEBHOOK_URL=your_discord_webhook

# Private League (Optional)
ESPN_S2=your_espn_s2_cookie
SWID=your_swid

# Feature Flags
TOP_HALF_SCORING=false
RANDOM_PHRASE=false
MONITOR_REPORT=true
WAIVER_REPORT=true
DAILY_WAIVER=false

# Messages
INIT_MSG=Fantasy Football Bot is ready!
```

## 📊 Monitoring & Logging

### Application Monitoring

#### Heroku Metrics
```bash
# View app metrics
heroku logs --tail --app your-bot-name

# Monitor resource usage
heroku ps --app your-bot-name

# View scheduler status
heroku addons:create scheduler:standard
```

#### Docker Container Monitoring
```bash
# View container logs
docker logs -f fantasy-football-bot

# Monitor resource usage
docker stats fantasy-football-bot

# Health checks
docker exec fantasy-football-bot python -c "from gamedaybot.espn.espn_bot import espn_bot; print('Bot is healthy')"
```

### Log Management

#### Structured Logging Setup
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        return json.dumps(log_obj)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

## 🛡️ Security Best Practices

### Environment Security
```bash
# Never commit secrets to git
echo ".env" >> .gitignore
echo "*.pem" >> .gitignore
echo "secrets/" >> .gitignore

# Use secret management systems
# Heroku: Config Vars
# AWS: Systems Manager Parameter Store
# Azure: Key Vault
# GCP: Secret Manager
```

### Container Security
```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Use specific base image versions
FROM python:3.9.16-slim

# Scan for vulnerabilities
RUN pip audit

# Multi-stage builds to reduce attack surface
FROM python:3.9-slim as builder
# Install dependencies
FROM python:3.9-slim as runtime
COPY --from=builder /app /app
```

## 🚨 Troubleshooting Deployment Issues

### Common Deployment Problems

#### 1. Environment Variables Not Set
```bash
# Check if variables are loaded
heroku config --app your-bot-name

# Test environment loading
heroku run --app your-bot-name "python -c 'import os; print(os.environ.get(\"LEAGUE_ID\"))'"
```

#### 2. ESPN API Connection Issues
```bash
# Test ESPN connection
heroku run --app your-bot-name "python -c '
from espn_api.football import League
league = League(league_id=123456, year=2024)
print(f\"Connected to: {league.settings.name}\")
'"
```

#### 3. Chat Platform Webhook Failures
```bash
# Test webhook directly
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"Test message"}' \
  your_webhook_url
```

#### 4. Scheduler Not Running
```bash
# Check worker dyno is running
heroku ps --app your-bot-name

# Check logs for scheduler errors
heroku logs --tail --app your-bot-name | grep -i scheduler
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **Single Instance**: Sufficient for most leagues (10-20 teams)
- **Multiple Instances**: Not recommended (scheduler conflicts)
- **Load Balancing**: Not applicable (cron-based execution)

### Resource Requirements
- **Memory**: 128-512 MB RAM
- **CPU**: 0.1-0.5 CPU cores
- **Network**: Outbound HTTPS only
- **Storage**: No persistent storage needed

This deployment guide covers all major deployment scenarios and provides comprehensive troubleshooting information for successful bot deployment.