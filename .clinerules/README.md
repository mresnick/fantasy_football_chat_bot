# Fantasy Football Chat Bot - Cline Rules

This directory contains comprehensive documentation to help AI assistants understand and work effectively with this fantasy football chat bot codebase.

## 📁 Directory Structure

- [`project-overview.md`](./project-overview.md) - High-level project description, purpose, and key features
- [`architecture.md`](./architecture.md) - Technical architecture, components, and design patterns
- [`development-guide.md`](./development-guide.md) - Development setup, workflows, and best practices
- [`deployment.md`](./deployment.md) - Deployment processes and CI/CD information
- [`testing.md`](./testing.md) - Testing strategies, frameworks, and guidelines
- [`environment-config.md`](./environment-config.md) - Environment variables and configuration management
- [`file-structure.md`](./file-structure.md) - Detailed explanation of the project's file organization

## 🚀 Quick Start for AI Assistants

1. **Understanding the Project**: Start with [`project-overview.md`](./project-overview.md)
2. **Technical Context**: Review [`architecture.md`](./architecture.md) for system design
3. **Making Changes**: Follow [`development-guide.md`](./development-guide.md) for workflows
4. **Deployment**: Check [`deployment.md`](./deployment.md) for deployment considerations

## 🎯 Project Summary

This is a Python-based ESPN Fantasy Football chat bot that:
- Integrates with ESPN Fantasy Football API
- Sends automated messages to GroupMe, Slack, and Discord
- Provides scheduled reports on scores, standings, power rankings, and more
- Supports slash commands via Discord bot integration
- Runs on a cron scheduler for automated messaging

## 🛠️ Key Technologies

- **Language**: Python 3.x
- **Framework**: espn_api for ESPN integration
- **Chat Platforms**: GroupMe, Slack, Discord
- **Scheduling**: APScheduler
- **Deployment**: Docker, Heroku, GitHub Actions
- **Testing**: pytest

## 📋 Common Tasks

- **Adding new functionality**: Modify [`gamedaybot/espn/functionality.py`](../gamedaybot/espn/functionality.py)
- **Scheduling changes**: Update [`gamedaybot/espn/scheduler.py`](../gamedaybot/espn/scheduler.py)
- **Chat platform integration**: Work with files in [`gamedaybot/chat/`](../gamedaybot/chat/)
- **Discord commands**: Extend [`gamedaybot/chat/discord_bot.py`](../gamedaybot/chat/discord_bot.py)