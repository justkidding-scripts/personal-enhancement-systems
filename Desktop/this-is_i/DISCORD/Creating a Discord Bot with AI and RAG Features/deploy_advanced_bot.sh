#!/bin/bash

# Advanced Discord Bot Deployment Script
# Deploys the full-featured Discord bot with all advanced capabilities

set -e  # Exit on any error

echo "🚀 Starting Advanced Discord Bot Deployment..."

# Configuration
BOT_USER="discordbot"
BOT_DIR="/home/$BOT_USER/discord-bot"
GITHUB_TOKEN="${GITHUB_TOKEN:-your_github_token_here}"
REPO_URL="https://$GITHUB_TOKEN@github.com/justkidding-scripts/discord-bot-vps.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Step 1: System Updates and Dependencies
log "Step 1: Updating system and installing dependencies..."

apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git curl wget unzip htop nano vim \
    build-essential software-properties-common sqlite3 nmap \
    python3-dev libffi-dev libssl-dev

# Install Node.js (for potential Discord CLI integration)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs

log "✅ System dependencies installed"

# Step 2: Install Ollama
log "Step 2: Installing Ollama..."

if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    log "✅ Ollama installed"
else
    log "✅ Ollama already installed"
fi

# Create ollama service
cat > /etc/systemd/system/ollama.service << EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="HOME=/usr/share/ollama"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=default.target
EOF

# Create ollama user
if ! id "ollama" &>/dev/null; then
    useradd -r -s /bin/false -m -d /usr/share/ollama ollama
fi

systemctl daemon-reload
systemctl enable ollama
systemctl start ollama

log "✅ Ollama service configured and started"

# Step 3: Create Bot User and Directory
log "Step 3: Setting up bot user and directories..."

if ! id "$BOT_USER" &>/dev/null; then
    useradd -m -s /bin/bash $BOT_USER
    log "✅ Created user: $BOT_USER"
else
    log "✅ User $BOT_USER already exists"
fi

# Remove existing directory if it exists
if [ -d "$BOT_DIR" ]; then
    rm -rf "$BOT_DIR"
    log "🗑️ Removed existing bot directory"
fi

# Create fresh directory
sudo -u $BOT_USER mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

log "✅ Bot directory created: $BOT_DIR"

# Step 4: Clone Repository
log "Step 4: Cloning bot repository..."

sudo -u $BOT_USER git clone "$REPO_URL" .
log "✅ Repository cloned successfully"

# Step 5: Python Environment Setup
log "Step 5: Setting up Python virtual environment..."

sudo -u $BOT_USER python3 -m venv bot_env
sudo -u $BOT_USER ./bot_env/bin/pip install --upgrade pip

# Install Python dependencies
log "Installing Python packages..."
sudo -u $BOT_USER ./bot_env/bin/pip install discord.py requests python-dotenv \
    beautifulsoup4 feedparser ollama pillow aiohttp python-nmap psutil \
    matplotlib numpy sqlite3

log "✅ Python environment configured"

# Step 6: Environment Configuration
log "Step 6: Configuring environment variables..."

# Create .env file
cat > "$BOT_DIR/.env" << EOF
# Discord Bot Configuration
DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN:-your_discord_bot_token_here}

# Ollama Configuration
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434

# RAG Configuration
RAG_FETCH_INTERVAL_SECONDS=3600
RAG_DATA_FOLDER=./rag_data

# API Keys
PLANT_ID_API_KEY=${PLANT_ID_API_KEY:-your_plant_id_api_key_here}

# Advanced Features
ENABLE_DAILY_REFLECTION=true
ENABLE_RSS_FEEDS=true
ENABLE_XP_SYSTEM=true
ENABLE_TERMINAL_ACCESS=true
ENABLE_AI_FEATURES=true

# Security Settings
AUTHORIZED_USERS=[]
TERMINAL_WHITELIST=["ls", "pwd", "whoami", "date", "uptime", "df", "free", "ps", "nmap"]

# Scheduler Settings
DAILY_REFLECTION_TIME=16:00
RSS_UPDATE_TIMES=["08:00", "16:00", "00:00"]
EOF

chown $BOT_USER:$BOT_USER "$BOT_DIR/.env"
chmod 600 "$BOT_DIR/.env"

log "✅ Environment configuration created"

# Step 7: Create Required Directories
log "Step 7: Creating required directories..."

sudo -u $BOT_USER mkdir -p "$BOT_DIR/rag_data"
sudo -u $BOT_USER mkdir -p "$BOT_DIR/logs"
sudo -u $BOT_USER mkdir -p "$BOT_DIR/data"
sudo -u $BOT_USER mkdir -p "$BOT_DIR/temp"

log "✅ Required directories created"

# Step 8: Download Ollama Models
log "Step 8: Downloading Ollama models..."

# Wait for Ollama to be ready
sleep 10

# Pull required models
ollama pull llama3.2:latest
ollama pull llama3.2:3b
ollama pull codellama:latest

log "✅ Ollama models downloaded"

# Step 9: Database Initialization
log "Step 9: Initializing databases..."

# Create initialization script
cat > "$BOT_DIR/init_databases.py" << 'EOF'
#!/usr/bin/env python3
import sqlite3
import os
from pathlib import Path

def init_all_databases():
    """Initialize all required databases"""
    
    # XP System Database
    xp_db = Path("data/xp_system.db")
    xp_db.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(xp_db)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_xp (
            user_id INTEGER PRIMARY KEY,
            guild_id INTEGER,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            last_message TIMESTAMP,
            daily_bonus_claimed DATE,
            total_messages INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_text TEXT NOT NULL,
            reward TEXT,
            deadline TIMESTAMP,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Scheduler Database
    scheduler_db = Path("scheduler.db")
    
    conn = sqlite3.connect(scheduler_db)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT NOT NULL,
            user_id INTEGER,
            channel_id INTEGER,
            guild_id INTEGER,
            schedule_time TEXT,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            question TEXT NOT NULL,
            response TEXT,
            ai_analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ All databases initialized successfully")

if __name__ == "__main__":
    init_all_databases()
EOF

# Run database initialization
sudo -u $BOT_USER "$BOT_DIR/bot_env/bin/python" "$BOT_DIR/init_databases.py"

log "✅ Databases initialized"

# Step 10: Create Systemd Service
log "Step 10: Creating systemd service..."

cat > /etc/systemd/system/discord-bot.service << EOF
[Unit]
Description=Advanced Discord Bot Service
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=$BOT_USER
Group=$BOT_USER
WorkingDirectory=$BOT_DIR
Environment=PATH=$BOT_DIR/bot_env/bin
ExecStart=$BOT_DIR/bot_env/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:$BOT_DIR/logs/bot.log
StandardError=append:$BOT_DIR/logs/bot_error.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$BOT_DIR
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF

# Create log files
sudo -u $BOT_USER touch "$BOT_DIR/logs/bot.log"
sudo -u $BOT_USER touch "$BOT_DIR/logs/bot_error.log"

systemctl daemon-reload
systemctl enable discord-bot

log "✅ Systemd service created and enabled"

# Step 11: Create Management Scripts
log "Step 11: Creating management scripts..."

# Bot management script
cat > "$BOT_DIR/manage_bot.sh" << 'EOF'
#!/bin/bash

case "$1" in
    start)
        sudo systemctl start discord-bot
        echo "✅ Bot started"
        ;;
    stop)
        sudo systemctl stop discord-bot
        echo "🛑 Bot stopped"
        ;;
    restart)
        sudo systemctl restart discord-bot
        echo "🔄 Bot restarted"
        ;;
    status)
        sudo systemctl status discord-bot
        ;;
    logs)
        tail -f /home/discordbot/discord-bot/logs/bot.log
        ;;
    errors)
        tail -f /home/discordbot/discord-bot/logs/bot_error.log
        ;;
    update)
        cd /home/discordbot/discord-bot
        sudo systemctl stop discord-bot
        sudo -u discordbot git pull
        sudo -u discordbot ./bot_env/bin/pip install -r requirements.txt
        sudo systemctl start discord-bot
        echo "🔄 Bot updated and restarted"
        ;;
    setup)
        echo "🚀 Running bot setup..."
        sudo -u discordbot ./bot_env/bin/python -c "
from commands.setup_commands import *
print('Setup commands loaded. Use Discord /setupbot command.')
"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|errors|update|setup}"
        exit 1
        ;;
esac
EOF

chmod +x "$BOT_DIR/manage_bot.sh"

# Create update script
cat > "$BOT_DIR/update_bot.sh" << 'EOF'
#!/bin/bash
echo "🔄 Updating Discord Bot..."

cd /home/discordbot/discord-bot

# Stop bot
sudo systemctl stop discord-bot

# Pull latest changes
sudo -u discordbot git pull

# Update dependencies
sudo -u discordbot ./bot_env/bin/pip install -r requirements.txt --upgrade

# Restart bot
sudo systemctl start discord-bot

echo "✅ Bot updated successfully!"
EOF

chmod +x "$BOT_DIR/update_bot.sh"

log "✅ Management scripts created"

# Step 12: Set Permissions
log "Step 12: Setting file permissions..."

chown -R $BOT_USER:$BOT_USER "$BOT_DIR"
chmod -R 755 "$BOT_DIR"
chmod 600 "$BOT_DIR/.env"

log "✅ File permissions set"

# Step 13: Start Services
log "Step 13: Starting services..."

# Start Ollama if not running
if ! systemctl is-active --quiet ollama; then
    systemctl start ollama
    sleep 5
fi

# Start Discord bot
systemctl start discord-bot

log "✅ Services started"

# Step 14: Verification
log "Step 14: Verifying deployment..."

sleep 10

# Check Ollama status
if systemctl is-active --quiet ollama; then
    log "✅ Ollama service is running"
else
    error "❌ Ollama service failed to start"
fi

# Check Discord bot status
if systemctl is-active --quiet discord-bot; then
    log "✅ Discord bot service is running"
else
    error "❌ Discord bot service failed to start"
    warn "Check logs with: journalctl -u discord-bot -f"
fi

# Display service status
echo ""
echo "📊 Service Status:"
echo "=================="
systemctl status ollama --no-pager -l
echo ""
systemctl status discord-bot --no-pager -l

# Step 15: Final Instructions
echo ""
echo "🎉 Advanced Discord Bot Deployment Complete!"
echo "=============================================="
echo ""
echo "📋 Management Commands:"
echo "• Start bot:    $BOT_DIR/manage_bot.sh start"
echo "• Stop bot:     $BOT_DIR/manage_bot.sh stop"
echo "• Restart bot:  $BOT_DIR/manage_bot.sh restart"
echo "• View logs:    $BOT_DIR/manage_bot.sh logs"
echo "• Update bot:   $BOT_DIR/manage_bot.sh update"
echo ""
echo "📊 System Status:"
echo "• Ollama:       $(systemctl is-active ollama)"
echo "• Discord Bot:  $(systemctl is-active discord-bot)"
echo ""
echo "🔧 Configuration:"
echo "• Bot Directory: $BOT_DIR"
echo "• Log Files:     $BOT_DIR/logs/"
echo "• Environment:   $BOT_DIR/.env"
echo ""
echo "🚀 Discord Commands to Try:"
echo "• /setupbot     - Complete bot configuration"
echo "• /testfeatures - Test all bot features"
echo "• /help         - Show all available commands"
echo "• /goodtalk     - Start AI conversation"
echo "• /xp           - Check your XP level"
echo ""
echo "📖 Next Steps:"
echo "1. Join your Discord server"
echo "2. Run /setupbot to configure all features"
echo "3. Use /testfeatures to verify everything works"
echo "4. Enjoy your advanced AI-powered Discord bot!"
echo ""

log "🎯 Deployment completed successfully!"
