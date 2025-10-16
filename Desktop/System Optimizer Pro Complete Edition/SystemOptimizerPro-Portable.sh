#!/bin/bash

# System Optimizer Pro Complete Edition - Portable Launcher
# This creates a self-contained portable version

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="SystemOptimizerComplete.py"
APP_PATH="$SCRIPT_DIR/$APP_NAME"

echo "🚀 System Optimizer Pro Complete Edition - Portable"
echo "=================================================="
echo "Starting from: $SCRIPT_DIR"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3 to run this application."
    exit 1
fi

# Check if the main app exists
if [ ! -f "$APP_PATH" ]; then
    echo "❌ Main application not found: $APP_PATH"
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."

# Check for tkinter
python3 -c "import tkinter" 2>/dev/null || {
    echo "⚠️ tkinter not found - installing..."
    sudo apt install -y python3-tk
}

# Check for psutil
python3 -c "import psutil" 2>/dev/null || {
    echo "⚠️ psutil not found - installing..."
    pip3 install psutil
}

echo "✅ Dependencies checked!"
echo ""

# Set environment variables for better compatibility
export DISPLAY="${DISPLAY:-:0}"

# Change to app directory
cd "$SCRIPT_DIR"

# Launch the application
echo "🎯 Launching System Optimizer Pro..."
python3 "$APP_NAME"

echo ""
echo "System Optimizer Pro has closed."