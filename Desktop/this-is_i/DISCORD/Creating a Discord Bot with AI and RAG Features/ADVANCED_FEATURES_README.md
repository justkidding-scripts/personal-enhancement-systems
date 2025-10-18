# 🚀 Advanced Discord Bot - Complete Feature Guide

## 🌟 Overview

This is a comprehensive AI-powered Discord bot with advanced features including personal AI assistance, Danish specialized commands, utility management, terminal integration, and much more. The bot uses Ollama for AI capabilities and includes a sophisticated RAG (Retrieval-Augmented Generation) system.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Personal AI Features](#personal-ai-features)
3. [Danish Advanced Features](#danish-advanced-features)
4. [Utility & Management](#utility--management)
5. [Terminal & CLI Integration](#terminal--cli-integration)
6. [Setup & Configuration](#setup--configuration)
7. [Deployment](#deployment)
8. [Command Reference](#command-reference)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed and running
- Discord Bot Token
- VPS or local machine

### Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/discord-bot-advanced.git
cd discord-bot-advanced

# Run the deployment script (VPS)
chmod +x deploy_advanced_bot.sh
sudo ./deploy_advanced_bot.sh

# Or manual setup (Local)
python3 -m venv bot_env
source bot_env/bin/activate
pip install -r requirements.txt
python main.py
```

### First Setup
1. Join your Discord server with the bot
2. Run `/setupbot` to configure all features
3. Use `/testfeatures` to verify everything works
4. Start using advanced commands!

## 🤖 Personal AI Features

### Daily Reflection System
- **Automatic Daily Prompt**: At 16:00 CET, the bot asks "What is important today?"
- **AI Analysis**: Your responses are analyzed by Ollama for insights
- **RAG Integration**: All reflections are stored in the knowledge base

**Commands:**
- `/whatisimportant` - Manual daily reflection
- `/compileme` - Get AI insights on your reflection data
- `/creativeai` - Get creative suggestions based on your knowledge

### AI Conversation Features
- **Continuous Chat**: `/goodtalk` - Start unlimited conversation with AI
- **Collaborative Coding**: `/aicode` - Build code together with AI
- **Psychology Sessions**: `/psychology` - AI therapy and counseling
- **Mind-Blowing Facts**: `/blowmymind` - Get amazing information
- **Life Insights**: `/lifeofmeaning` - Philosophical discussions

### Wealth & Success
- `/greedisgood` - Daily wealth-building advice based on your data

### Real-time Context
- The AI always responds considering ALL server information and RAG data
- Fetches real-time information from all Discord channels

## 🇩🇰 Danish Advanced Features

### Gaming & Simulation
- **Dynamic Quest Generator**: Real-time RPG quests based on server activity
- **"Hvad hvis" Game**: Historical/hypothetical scenario simulations
- **Red vs Blue Simulation**: Full cybersecurity battle simulation

### AI-Powered Systems
- **AI Debate Moderator**: Facilitates and summarizes complex debates
- **AI-Driven Economy**: Decentralized server economy with AI-controlled currency
- **Personalized Learning Paths**: Custom education tracks designed by AI
- **Chain-of-Thought Reasoning**: See AI's complete thought process

### Security & OSINT
- **Nmap Integration**: Network scanning as Discord commands
- `/OSINTAI` - Collaborative Open Source Intelligence work
- `/redteam1` - Prompt chaining for security analysis
- `/payloadstego` - Steganography payload creation
- `/gophish` - AI-generated phishing scenarios (authorized testing)

### Advanced Automation
- **Automated API Interaction**: Complex multi-step API workflows
- **Document Analysis**: Upload documents for AI summary and questions
- **Custom Commands**: Users can create their own simple commands
- `/integratepromt` - Insert permanent prompts into AI context

## 🛠️ Utility & Management

### XP & Leveling System
- **Automatic XP**: Earn 5 XP per message
- **Daily Bonuses**: 50 XP daily bonus
- **Leaderboards**: Server-wide ranking system
- **Achievement Notifications**: Level-up celebrations

**Commands:**
- `/xp` - Check your current XP and level
- `/daily` - Claim daily XP bonus
- `/leaderboard` - View server rankings

### Goal Tracking
- `/goalfam` - Set personal goals with rewards and deadlines
- `/mygoals` - Track your progress
- Automatic reminders and achievement celebrations

### RSS News Feeds
- **Unbiased Sources**: BBC, Reuters, AP News, NPR, The Guardian
- **3x Daily Updates**: Every 8 hours
- **Smart Filtering**: AI-curated relevant news

### Image & Media
- **AI Image Generation**: Create images from text descriptions
- **Custom Emojis/Stickers**: Server-specific media management
- **Plant Identification**: Upload plant photos for AI identification

### Daily Rewards
- **Daily Login Bonuses**: XP, coins, and special rewards
- **Streak Tracking**: Consecutive day bonuses
- **Special Events**: Holiday and milestone rewards

## 💻 Terminal & CLI Integration

### Secure Terminal Access
- **Whitelisted Commands**: Only safe, pre-approved commands
- **Security Logging**: All terminal activity logged
- **User Authorization**: Role-based access control

**Available Commands:**
```bash
ls, pwd, whoami, date, uptime, df, free, ps, nmap, git status
```

### Discord CLI Integration
- `/channelexport` - Export entire channel as text file
- `/wipemyass` - Remove your messages from today in a channel
- **Real-time Channel Monitoring**: Fetch live data from all channels

### System Monitoring
- **Server Stats**: CPU, memory, disk usage
- **Bot Health**: Service status and performance metrics
- **Log Analysis**: Real-time log monitoring and alerts

## ⚙️ Setup & Configuration

### Initial Setup Wizard
```discord
/setupbot
```
This comprehensive wizard configures:
1. Daily reflection prompts (16:00 CET)
2. RSS news feeds (3x daily)
3. XP and leveling system
4. AI features and model selection
5. Terminal access permissions
6. Feature testing and verification

### Quick Setup (Experienced Users)
```discord
/quicksetup
```
Instantly configures all features with default settings.

### Configuration Management
- `/botconfig` - View current configuration
- `/testfeatures` - Run diagnostic tests
- `/resetbot` - Reset all configuration (admin only)

### Environment Variables
```env
# Core Configuration
DISCORD_BOT_TOKEN=your_token_here
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434

# Feature Toggles
ENABLE_DAILY_REFLECTION=true
ENABLE_RSS_FEEDS=true
ENABLE_XP_SYSTEM=true
ENABLE_TERMINAL_ACCESS=true

# Security
AUTHORIZED_USERS=["user_id_1", "user_id_2"]
TERMINAL_WHITELIST=["ls", "pwd", "whoami"]

# Scheduling
DAILY_REFLECTION_TIME=16:00
RSS_UPDATE_TIMES=["08:00", "16:00", "00:00"]
```

## 🚀 Deployment

### VPS Deployment (Recommended)
```bash
# Download and run the deployment script
wget https://raw.githubusercontent.com/your-repo/discord-bot/main/deploy_advanced_bot.sh
chmod +x deploy_advanced_bot.sh
sudo ./deploy_advanced_bot.sh
```

The script automatically:
- Installs all dependencies
- Sets up Ollama with required models
- Creates systemd services
- Configures security settings
- Initializes databases
- Starts all services

### Manual Deployment
1. **System Dependencies**:
   ```bash
   apt update && apt install python3 python3-pip python3-venv git curl
   ```

2. **Ollama Installation**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama serve &
   ollama pull llama3.2:latest
   ```

3. **Bot Setup**:
   ```bash
   git clone your-repo
   cd discord-bot
   python3 -m venv bot_env
   source bot_env/bin/activate
   pip install -r requirements.txt
   ```

4. **Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your tokens and settings
   ```

5. **Run**:
   ```bash
   python main.py
   ```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
```

### Service Management
```bash
# Start/stop services
sudo systemctl start discord-bot
sudo systemctl stop discord-bot
sudo systemctl restart discord-bot

# View logs
sudo journalctl -u discord-bot -f

# Update bot
./manage_bot.sh update
```

## 📚 Command Reference

### Personal AI Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/whatisimportant` | Daily reflection prompt | `/whatisimportant` |
| `/compileme` | AI analysis of your data | `/compileme` |
| `/creativeai` | Creative suggestions | `/creativeai [topic]` |
| `/goodtalk` | Continuous AI conversation | `/goodtalk` |
| `/aicode` | Collaborative coding | `/aicode [language]` |
| `/psychology` | AI therapy session | `/psychology` |
| `/blowmymind` | Amazing facts | `/blowmymind [category]` |
| `/lifeofmeaning` | Life insights | `/lifeofmeaning` |
| `/greedisgood` | Wealth advice | `/greedisgood` |

### Danish Advanced Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/OSINTAI` | OSINT collaboration | `/OSINTAI [target]` |
| `/redteam1` | Security analysis | `/redteam1 [target]` |
| `/payloadstego` | Steganography tools | `/payloadstego [file]` |
| `/gophish` | Phishing scenarios | `/gophish [template]` |
| `/integratepromt` | Add permanent prompt | `/integratepromt [text]` |

### Utility Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/xp` | Check XP/level | `/xp [@user]` |
| `/daily` | Daily XP bonus | `/daily` |
| `/leaderboard` | XP rankings | `/leaderboard` |
| `/goalfam` | Set goal | `/goalfam [goal] [reward] [deadline]` |
| `/mygoals` | View goals | `/mygoals` |
| `/rss` | Latest news | `/rss [source]` |

### Terminal Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/terminal` | Execute command | `/terminal [command]` |
| `/channelexport` | Export channel | `/channelexport [channel]` |
| `/wipemyass` | Delete your messages | `/wipemyass [channel]` |

### Setup Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `/setupbot` | Complete setup wizard | `/setupbot` |
| `/quicksetup` | Quick configuration | `/quicksetup` |
| `/testfeatures` | Test all features | `/testfeatures` |
| `/botconfig` | View configuration | `/botconfig` |
| `/resetbot` | Reset configuration | `/resetbot` |

## 🔧 Advanced Configuration

### Custom AI Models
```python
# In config.py
OLLAMA_MODELS = {
    "general": "llama3.2:latest",
    "coding": "codellama:latest",
    "creative": "llama3.2:3b"
}
```

### RAG System Tuning
```python
# RAG configuration
RAG_CHUNK_SIZE = 1000
RAG_OVERLAP = 200
RAG_MAX_RESULTS = 5
RAG_SIMILARITY_THRESHOLD = 0.7
```

### Security Settings
```python
# Security configuration
AUTHORIZED_ROLES = ["Admin", "Moderator"]
TERMINAL_TIMEOUT = 300  # 5 minutes
MAX_COMMAND_LENGTH = 100
RATE_LIMIT_COMMANDS = 10  # per minute
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Not Running**:
   ```bash
   sudo systemctl start ollama
   ollama list  # Check available models
   ```

2. **Bot Not Responding**:
   ```bash
   sudo systemctl status discord-bot
   sudo journalctl -u discord-bot -f
   ```

3. **Database Errors**:
   ```bash
   cd /home/discordbot/discord-bot
   python init_databases.py
   ```

4. **Permission Denied**:
   ```bash
   sudo chown -R discordbot:discordbot /home/discordbot/discord-bot
   ```

### Log Locations
- Bot logs: `/home/discordbot/discord-bot/logs/bot.log`
- Error logs: `/home/discordbot/discord-bot/logs/bot_error.log`
- System logs: `journalctl -u discord-bot`

### Performance Optimization
- Use SSD storage for databases
- Allocate sufficient RAM (minimum 2GB)
- Enable swap if memory is limited
- Use CDN for image generation
- Cache frequently accessed data

## 🤝 Contributing

### Development Setup
```bash
git clone your-repo
cd discord-bot
python -m venv dev_env
source dev_env/bin/activate
pip install -r requirements-dev.txt
```

### Adding New Commands
1. Create command file in `commands/` directory
2. Use the `@command` decorator
3. Test with `/testfeatures`
4. Update documentation

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Include error handling
- Write tests

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- Ollama team for the AI framework
- Discord.py developers
- Open source community
- Beta testers and contributors

---

**Need help?** Join our Discord server or create an issue on GitHub!

🚀 **Happy botting!** 🤖
