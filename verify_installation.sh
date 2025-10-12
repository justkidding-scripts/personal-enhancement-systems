#!/bin/bash
# System Verification Script - Test all Enhancement Systems components

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
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
echo -e "${BLUE}🧪 Enhancement Systems Verification${NC}"
echo "=================================="
echo ""

# Test 1: Check required files
print_status "Checking required files..."
REQUIRED_FILES=(
    "tesseract_timeout_fix_working.py"
    "integrate_ocr_timeout_fix.py" 
    "advanced_enhancement_system.py"
    "enhancement_manager.py"
    "enhance"
    "Desktop/Enhancement_Systems_Launcher.py"
    "setup_enhancement_systems.sh"
    "ENHANCEMENT_SYSTEMS_README.md"
    "QUICK_START_GUIDE.md"
)

missing_files=0
for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
        ((missing_files++))
    fi
done

# Test 2: Check system dependencies
print_status "Checking system dependencies..."
SYSTEM_DEPS=("tesseract" "python3" "git")

missing_deps=0
for dep in "${SYSTEM_DEPS[@]}"; do
    if command -v "$dep" >/dev/null 2>&1; then
        version=$($dep --version 2>&1 | head -n1)
        print_success "$dep: $version"
    else
        print_error "Missing system dependency: $dep"
        ((missing_deps++))
    fi
done

# Test 3: Check Python packages  
print_status "Checking Python packages..."
PYTHON_PACKAGES=("pytesseract" "PIL" "psutil")

missing_py_packages=0
for package in "${PYTHON_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        print_success "Python package: $package"
    else
        print_error "Missing Python package: $package"
        ((missing_py_packages++))
    fi
done

# Test 4: Test executable permissions
print_status "Checking executable permissions..."
EXECUTABLE_FILES=("enhance" "setup_enhancement_systems.sh" "Desktop/Enhancement_Systems_Launcher.py")

perm_issues=0
for file in "${EXECUTABLE_FILES[@]}"; do
    if [[ -x "$file" ]]; then
        print_success "Executable: $file"
    else
        print_error "Not executable: $file"
        ((perm_issues++))
    fi
done

# Test 5: Test individual systems
print_status "Testing individual systems..."

test_failures=0

# Test OCR fix
print_status "Testing OCR timeout fix..."
if timeout 10s python3 tesseract_timeout_fix_working.py >/dev/null 2>&1; then
    print_success "OCR timeout fix working"
else
    print_warning "OCR timeout fix test failed or timed out"
    ((test_failures++))
fi

# Test enhancement manager
print_status "Testing enhancement manager..."
if python3 enhancement_manager.py overview >/dev/null 2>&1; then
    print_success "Enhancement manager working"
else
    print_error "Enhancement manager test failed"
    ((test_failures++))
fi

# Test advanced enhancement system
print_status "Testing advanced enhancement system..."
if timeout 5s python3 advanced_enhancement_system.py >/dev/null 2>&1; then
    print_success "Advanced enhancement system working"
else
    print_warning "Advanced enhancement system test failed or timed out"
    ((test_failures++))
fi

# Test 6: Check Git repository
print_status "Checking Git repository..."
if [[ -d ".git" ]]; then
    print_success "Git repository initialized"
    
    # Check for commits
    if git log --oneline >/dev/null 2>&1; then
        commit_count=$(git rev-list --count HEAD)
        print_success "Git repository has $commit_count commit(s)"
    else
        print_warning "Git repository has no commits"
    fi
else
    print_error "Git repository not initialized"
fi

# Test 7: Check aliases
print_status "Checking shell aliases..."
if grep -q "Personal Enhancement Systems" ~/.bashrc 2>/dev/null || grep -q "Personal Enhancement Systems" ~/.zshrc 2>/dev/null; then
    print_success "Shell aliases configured"
else
    print_warning "Shell aliases not found in .bashrc or .zshrc"
fi

# Summary
echo ""
echo -e "${BLUE}📊 Verification Summary${NC}"
echo "======================"

total_issues=$((missing_files + missing_deps + missing_py_packages + perm_issues + test_failures))

if [[ $total_issues -eq 0 ]]; then
    print_success "ALL TESTS PASSED! 🎉"
    echo ""
    echo "Your Enhancement Systems are fully operational!"
    echo ""
    echo "Quick start options:"
    echo "1. Double-click 'Enhancement Systems Launcher' on desktop"
    echo "2. Run: ./enhance overview"
    echo "3. Run: ./setup_enhancement_systems.sh (if you need to reconfigure)"
    echo ""
else
    print_warning "Issues found: $total_issues"
    echo ""
    echo "Issue breakdown:"
    [[ $missing_files -gt 0 ]] && echo "- Missing files: $missing_files"
    [[ $missing_deps -gt 0 ]] && echo "- Missing system dependencies: $missing_deps"
    [[ $missing_py_packages -gt 0 ]] && echo "- Missing Python packages: $missing_py_packages"
    [[ $perm_issues -gt 0 ]] && echo "- Permission issues: $perm_issues"
    [[ $test_failures -gt 0 ]] && echo "- Test failures: $test_failures"
    echo ""
    echo "Recommended fixes:"
    echo "1. Run: ./setup_enhancement_systems.sh"
    echo "2. Or use the Desktop Launcher's Setup tab"
    echo "3. Check the QUICK_START_GUIDE.md for troubleshooting"
fi

echo ""
echo "Verification complete!"

exit $total_issues