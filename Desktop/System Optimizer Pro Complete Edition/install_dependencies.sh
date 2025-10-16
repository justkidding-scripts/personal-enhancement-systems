#!/bin/bash

echo "🚀 Installing System Optimizer Pro Dependencies..."
echo "=================================================="

# Update package lists
echo "📦 Updating package lists..."
sudo apt update

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-tk python3-psutil

# Install system utilities
echo "🛠️ Installing system utilities..."
sudo apt install -y xdg-utils gnome-text-editor curl wget git

# Install additional tools for diagnostics
echo "🔧 Installing diagnostic tools..."
sudo apt install -y sensors lm-sensors smartmontools

# Setup icon cache
echo "🎨 Setting up icon cache..."
gtk-update-icon-cache -f ~/.local/share/icons/hicolor/ 2>/dev/null || true
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

# Set proper permissions
echo "🔒 Setting permissions..."
chmod +x "$(dirname "$0")/SystemOptimizerComplete.py"
chmod +x "$(dirname "$0")/SystemOptimizerPro.desktop"

echo ""
echo "✅ Installation complete!"
echo "You can now run System Optimizer Pro Complete Edition"
echo ""
echo "Usage:"
echo "  • Double-click SystemOptimizerPro.desktop"
echo "  • Or run: python3 SystemOptimizerComplete.py"
echo ""