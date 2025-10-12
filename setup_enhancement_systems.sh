#!/bin/bash
# Complete Enhancement Systems Setup Script
# One-click setup for all personal enhancement systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Header
clear
echo -e "${BLUE}🚀 Personal Enhancement Systems Setup${NC}"
echo "======================================"
echo "This script will:"
echo "1. Install all required dependencies"
echo "2. Set up all enhancement systems"
echo "3. Create desktop launcher"
echo "4. Configure Git repository"
echo "5. Push to GitHub (optional)"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "Please don't run this script as root"
    exit 1
fi

# System information
print_status "Detecting system..."
OS=$(lsb_release -si 2>/dev/null || echo "Unknown")
VERSION=$(lsb_release -sr 2>/dev/null || echo "Unknown")
print_success "Running on: $OS $VERSION"

# Step 1: Update system and install dependencies
print_status "Step 1: Installing system dependencies..."
sudo apt update

# Install system packages
SYSTEM_PACKAGES=(
    "tesseract-ocr"
    "python3-tk"
    "git"
    "python3-pip"
    "python3-dev"
    "build-essential"
    "curl"
    "wget"
)

for package in "${SYSTEM_PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $package "; then
        print_status "Installing $package..."
        sudo apt install -y "$package"
    else
        print_success "$package already installed"
    fi
done

# Step 2: Install Python packages
print_status "Step 2: Installing Python dependencies..."
PYTHON_PACKAGES=(
    "pytesseract"
    "pillow"
    "psutil"
    "requests"
    "rich"
)

for package in "${PYTHON_PACKAGES[@]}"; do
    print_status "Installing Python package: $package"
    python3 -m pip install --user --break-system-packages "$package" || {
        print_warning "Failed to install $package with --break-system-packages, trying without..."
        python3 -m pip install --user "$package"
    }
done

# Step 3: Ensure all enhancement system files are present
print_status "Step 3: Setting up enhancement systems..."

HOME_DIR="/home/$(whoami)"
SYSTEMS_DIR="$HOME_DIR"

# List of required files
REQUIRED_FILES=(
    "tesseract_timeout_fix_working.py"
    "integrate_ocr_timeout_fix.py"
    "advanced_enhancement_system.py"
    "enhancement_manager.py"
    "ENHANCEMENT_SYSTEMS_README.md"
)

# Check if files exist
missing_files=()
for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$SYSTEMS_DIR/$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    print_warning "Missing files: ${missing_files[*]}"
    print_status "Files should be in: $SYSTEMS_DIR"
    print_warning "Please ensure all enhancement system files are in place"
else
    print_success "All enhancement system files found!"
fi

# Step 4: Create launcher and desktop integration
print_status "Step 4: Setting up desktop integration..."

# Make launcher script executable
if [[ -f "$HOME_DIR/enhance" ]]; then
    chmod +x "$HOME_DIR/enhance"
    print_success "Made enhance launcher executable"
fi

# Create desktop shortcut for GUI launcher
DESKTOP_DIR="$HOME_DIR/Desktop"
DESKTOP_SHORTCUT="$DESKTOP_DIR/Enhancement_Systems_Launcher.desktop"

if [[ -f "$DESKTOP_DIR/Enhancement_Systems_Launcher.py" ]]; then
    cat > "$DESKTOP_SHORTCUT" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Enhancement Systems Launcher
Comment=Personal Enhancement Systems - One-click installer and launcher
Icon=applications-system
Exec=python3 "$DESKTOP_DIR/Enhancement_Systems_Launcher.py"
Path=$DESKTOP_DIR
Terminal=false
Categories=Development;System;Utility;
EOF
    
    chmod +x "$DESKTOP_SHORTCUT"
    print_success "Created desktop shortcut"
else
    print_warning "GUI launcher not found at $DESKTOP_DIR/Enhancement_Systems_Launcher.py"
fi

# Step 5: Update bashrc with aliases
print_status "Step 5: Setting up shell aliases..."

BASHRC_FILE="$HOME_DIR/.bashrc"
ZSHRC_FILE="$HOME_DIR/.zshrc"

# Determine which shell config to use
SHELL_CONFIG=""
if [[ "$SHELL" == *"zsh"* ]] && [[ -f "$ZSHRC_FILE" ]]; then
    SHELL_CONFIG="$ZSHRC_FILE"
    print_status "Detected zsh shell, using .zshrc"
elif [[ -f "$BASHRC_FILE" ]]; then
    SHELL_CONFIG="$BASHRC_FILE"
    print_status "Using .bashrc for shell configuration"
fi

if [[ -n "$SHELL_CONFIG" ]]; then
    # Check if aliases already exist
    if ! grep -q "# Personal Enhancement Systems" "$SHELL_CONFIG"; then
        cat >> "$SHELL_CONFIG" << 'EOF'

# Personal Enhancement Systems
export PATH="/home/nike:$PATH"
alias enhance-overview="python3 /home/nike/enhancement_manager.py overview"
alias enhance-monitor="python3 /home/nike/advanced_enhancement_system.py monitor"
alias enhance-report="python3 /home/nike/advanced_enhancement_system.py report"
alias enhance-analyze="python3 /home/nike/advanced_enhancement_system.py analyze"
alias fix-ocr="python3 /home/nike/integrate_ocr_timeout_fix.py"
alias enhancement-gui="python3 /home/nike/Desktop/Enhancement_Systems_Launcher.py"
EOF
        print_success "Added shell aliases"
    else
        print_success "Shell aliases already configured"
    fi
else
    print_warning "Could not determine shell configuration file"
fi

# Step 6: Test systems
print_status "Step 6: Testing systems..."

cd "$SYSTEMS_DIR"

# Test OCR fix
if [[ -f "tesseract_timeout_fix_working.py" ]]; then
    print_status "Testing OCR timeout fix..."
    timeout 30s python3 tesseract_timeout_fix_working.py > /dev/null 2>&1 && \
        print_success "OCR timeout fix working" || \
        print_warning "OCR timeout fix test failed or timed out"
fi

# Test enhancement manager
if [[ -f "enhancement_manager.py" ]]; then
    print_status "Testing enhancement manager..."
    python3 enhancement_manager.py overview > /dev/null 2>&1 && \
        print_success "Enhancement manager working" || \
        print_warning "Enhancement manager test failed"
fi

# Step 7: Git setup
print_status "Step 7: Setting up Git repository..."

# Initialize git if not already done
if [[ ! -d ".git" ]]; then
    git init
    print_success "Initialized Git repository"
    
    # Set user config if not set
    if ! git config user.name > /dev/null 2>&1; then
        git config user.name "Enhancement Systems User"
        git config user.email "enhancement@local.dev"
        print_success "Set Git user configuration"
    fi
else
    print_success "Git repository already initialized"
fi

# Create .gitignore
if [[ ! -f ".gitignore" ]]; then
    cat > .gitignore << 'EOF'
# Enhancement Systems .gitignore
*.pyc
__pycache__/
*.backup
.enhancement_system.db
*.log
.DS_Store
Thumbs.db
*.tmp
.vscode/
.idea/
EOF
    print_success "Created .gitignore file"
fi

# Add and commit files
print_status "Committing files to Git..."
git add .
if git diff --staged --quiet; then
    print_success "No changes to commit"
else
    git commit -m "Initial setup of Enhancement Systems - $(date +'%Y-%m-%d %H:%M:%S')"
    print_success "Committed changes to Git"
fi

# Step 8: GitHub setup (optional)
echo ""
echo -e "${YELLOW}GitHub Setup (Optional):${NC}"
read -p "Do you want to push to GitHub? (y/N): " push_github

if [[ "$push_github" =~ ^[Yy]$ ]]; then
    read -p "Enter your GitHub repository URL: " repo_url
    
    if [[ -n "$repo_url" ]]; then
        print_status "Setting up GitHub remote..."
        
        # Add remote if it doesn't exist
        if ! git remote get-url origin > /dev/null 2>&1; then
            git remote add origin "$repo_url"
            print_success "Added GitHub remote"
        fi
        
        # Push to GitHub
        print_status "Pushing to GitHub..."
        if git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null; then
            print_success "Successfully pushed to GitHub!"
        else
            print_warning "Failed to push to GitHub - you may need to authenticate or create the repository first"
            print_status "Visit: https://github.com/new to create a new repository"
        fi
    fi
else
    print_status "Skipping GitHub setup"
fi

# Step 9: Final summary
echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "=============================="
echo ""
echo "Available commands:"
echo "  enhance                    - Show all enhancement commands"
echo "  enhance overview           - Show system overview"  
echo "  enhance monitor            - Start continuous monitoring"
echo "  enhance analyze            - Analyze opportunities"
echo "  enhance report             - Generate reports"
echo "  enhance-gui                - Launch graphical interface"
echo ""
echo "Quick aliases:"
echo "  enhance-overview           - System overview"
echo "  enhance-monitor            - Start monitoring" 
echo "  enhance-report             - Generate report"
echo "  enhance-analyze            - Analyze opportunities"
echo "  fix-ocr                    - Fix OCR timeout issues"
echo ""
echo "Desktop:"
echo "  Double-click 'Enhancement Systems Launcher' on your desktop"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "  • Run 'source ~/.bashrc' or 'source ~/.zshrc' to activate aliases"
echo "  • Start with 'enhance analyze' to see your opportunities"
echo "  • Use 'enhance monitor' for continuous productivity tracking"
echo "  • The GUI launcher provides an easy point-and-click interface"
echo ""

if [[ ${#missing_files[@]} -eq 0 ]]; then
    print_success "All systems are ready to use!"
else
    print_warning "Some files are missing - please ensure all enhancement scripts are in place"
fi

echo ""
echo "Setup log saved to: $(pwd)/setup.log"
echo "Documentation available in: ENHANCEMENT_SYSTEMS_README.md"
echo ""
echo -e "${GREEN}Happy enhancing! 🚀${NC}"