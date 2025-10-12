#!/usr/bin/env python3
"""
Enhancement System Manager
Central control hub for all personal enhancement tools
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import argparse

class EnhancementManager:
    """Central manager for all enhancement systems"""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.systems = {
            'ocr_fix': {
                'name': 'OCR Timeout Fix',
                'description': 'Fixes OCR timeout issues in existing projects',
                'script': 'tesseract_timeout_fix_working.py',
                'test_command': 'python tesseract_timeout_fix_working.py',
                'status': 'available'
            },
            'ocr_integration': {
                'name': 'OCR Integration Tool',
                'description': 'Automatically integrates OCR fixes into existing code',
                'script': 'integrate_ocr_timeout_fix.py',
                'test_command': 'python integrate_ocr_timeout_fix.py',
                'status': 'available'
            },
            'advanced_enhancement': {
                'name': 'Advanced Enhancement System',
                'description': 'Complete framework for productivity monitoring and optimization',
                'script': 'advanced_enhancement_system.py',
                'test_command': 'python advanced_enhancement_system.py',
                'commands': {
                    'monitor': 'Start continuous monitoring',
                    'analyze': 'Analyze enhancement opportunities',
                    'report': 'Generate comprehensive report',
                    'test-ocr': 'Test OCR capabilities'
                },
                'status': 'available'
            }
        }
        
        # Previously built systems (if they exist)
        self.legacy_systems = {
            'life_integration': {
                'name': 'Life Integration System',
                'script': 'warp_life_integration.py',
                'description': 'Correlates work habits with wellness metrics'
            },
            'unified_dashboard': {
                'name': 'Unified Personal Dashboard',
                'script': 'warp_unified_dashboard.py',
                'description': 'TUI dashboard combining all enhancement modules'
            },
            'analytics_engine': {
                'name': 'Personal Analytics Engine',
                'script': 'warp_personal_analytics.py',
                'description': 'Advanced analytics for personal productivity'
            },
            'income_optimizer': {
                'name': 'Income Optimization System',
                'script': 'warp_income_optimizer.py',
                'description': 'AI-powered income and career optimization'
            }
        }
    
    def check_system_status(self) -> Dict[str, Any]:
        """Check status of all enhancement systems"""
        status = {
            'available_systems': [],
            'missing_systems': [],
            'system_details': {}
        }
        
        # Check main systems
        for sys_id, sys_info in self.systems.items():
            script_path = self.home_dir / sys_info['script']
            if script_path.exists():
                status['available_systems'].append(sys_id)
                status['system_details'][sys_id] = {
                    **sys_info,
                    'path': str(script_path),
                    'size': script_path.stat().st_size,
                    'modified': datetime.fromtimestamp(script_path.stat().st_mtime).isoformat()
                }
            else:
                status['missing_systems'].append(sys_id)
        
        # Check legacy systems
        for sys_id, sys_info in self.legacy_systems.items():
            script_path = self.home_dir / sys_info['script']
            if script_path.exists():
                status['available_systems'].append(f"legacy_{sys_id}")
                status['system_details'][f"legacy_{sys_id}"] = {
                    **sys_info,
                    'path': str(script_path),
                    'legacy': True
                }
        
        return status
    
    def show_system_overview(self):
        """Display overview of all enhancement systems"""
        print("🚀 Personal Enhancement Systems Overview")
        print("=" * 60)
        
        status = self.check_system_status()
        
        print(f"📊 Status Summary:")
        print(f"├── Available Systems: {len(status['available_systems'])}")
        print(f"├── Missing Systems: {len(status['missing_systems'])}")
        print(f"└── Total Systems: {len(self.systems) + len(self.legacy_systems)}")
        
        print(f"\n✅ Available Systems:")
        for sys_id in status['available_systems']:
            if sys_id in status['system_details']:
                details = status['system_details'][sys_id]
                legacy_tag = " (Legacy)" if details.get('legacy') else ""
                print(f"  📄 {details['name']}{legacy_tag}")
                print(f"     {details['description']}")
                print(f"     Script: {details['script']}")
        
        if status['missing_systems']:
            print(f"\n⚠️ Missing Systems:")
            for sys_id in status['missing_systems']:
                sys_info = self.systems[sys_id]
                print(f"  ❌ {sys_info['name']}")
                print(f"     Script: {sys_info['script']}")
    
    def test_system(self, system_id: str) -> bool:
        """Test a specific enhancement system"""
        if system_id not in self.systems:
            print(f"❌ Unknown system: {system_id}")
            return False
        
        sys_info = self.systems[system_id]
        script_path = self.home_dir / sys_info['script']
        
        if not script_path.exists():
            print(f"❌ System script not found: {script_path}")
            return False
        
        print(f"🧪 Testing {sys_info['name']}...")
        
        try:
            # Run test command
            result = subprocess.run(
                sys_info['test_command'].split(),
                cwd=self.home_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ {sys_info['name']} test passed")
                print(f"Output preview: {result.stdout[:200]}...")
                return True
            else:
                print(f"❌ {sys_info['name']} test failed")
                print(f"Error: {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ {sys_info['name']} test timed out")
            return False
        except Exception as e:
            print(f"❌ Error testing {sys_info['name']}: {e}")
            return False
    
    def run_system(self, system_id: str, command: str = None):
        """Run a specific enhancement system"""
        if system_id not in self.systems:
            print(f"❌ Unknown system: {system_id}")
            return
        
        sys_info = self.systems[system_id]
        script_path = self.home_dir / sys_info['script']
        
        if not script_path.exists():
            print(f"❌ System script not found: {script_path}")
            return
        
        # Build command
        cmd_parts = ['python', sys_info['script']]
        if command:
            cmd_parts.append(command)
        
        print(f"🚀 Running {sys_info['name']}...")
        if command:
            print(f"Command: {command}")
        
        try:
            # Run interactively
            subprocess.run(cmd_parts, cwd=self.home_dir)
        except KeyboardInterrupt:
            print(f"\n⏹️ Stopped {sys_info['name']}")
        except Exception as e:
            print(f"❌ Error running {sys_info['name']}: {e}")
    
    def show_system_help(self, system_id: str):
        """Show help for a specific system"""
        if system_id not in self.systems:
            print(f"❌ Unknown system: {system_id}")
            return
        
        sys_info = self.systems[system_id]
        print(f"📖 Help for {sys_info['name']}")
        print("=" * 50)
        print(f"Description: {sys_info['description']}")
        print(f"Script: {sys_info['script']}")
        
        if 'commands' in sys_info:
            print(f"\n📋 Available Commands:")
            for cmd, desc in sys_info['commands'].items():
                print(f"  {cmd}: {desc}")
        
        print(f"\n💡 Usage Examples:")
        print(f"  python enhancement_manager.py run {system_id}")
        if 'commands' in sys_info:
            print(f"  python enhancement_manager.py run {system_id} <command>")
    
    def create_launcher_script(self):
        """Create convenience launcher script"""
        launcher_content = f"""#!/bin/bash
# Personal Enhancement Systems Launcher
# Auto-generated on {datetime.now().isoformat()}

SCRIPT_DIR="{self.home_dir}"

case "$1" in
    "overview"|"status")
        python3 "$SCRIPT_DIR/enhancement_manager.py" overview
        ;;
    "monitor")
        echo "🔍 Starting Advanced Monitoring..."
        python3 "$SCRIPT_DIR/advanced_enhancement_system.py" monitor
        ;;
    "analyze")
        echo "📊 Analyzing Enhancement Opportunities..."
        python3 "$SCRIPT_DIR/advanced_enhancement_system.py" analyze
        ;;
    "report")
        echo "📄 Generating Enhancement Report..."
        python3 "$SCRIPT_DIR/advanced_enhancement_system.py" report
        ;;
    "fix-ocr")
        echo "🔧 Running OCR Integration Fix..."
        python3 "$SCRIPT_DIR/integrate_ocr_timeout_fix.py"
        ;;
    "test-ocr")
        echo "🧪 Testing OCR System..."
        python3 "$SCRIPT_DIR/advanced_enhancement_system.py" test-ocr
        ;;
    *)
        echo "🚀 Personal Enhancement Systems"
        echo "Usage: enhance <command>"
        echo ""
        echo "Available commands:"
        echo "  overview    - Show system overview"
        echo "  monitor     - Start continuous monitoring"
        echo "  analyze     - Analyze opportunities"
        echo "  report      - Generate detailed report"
        echo "  fix-ocr     - Fix OCR timeout issues"
        echo "  test-ocr    - Test OCR capabilities"
        echo ""
        echo "For full management interface:"
        echo "  python3 enhancement_manager.py --help"
        ;;
esac
"""
        
        launcher_path = self.home_dir / "enhance"
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        
        print(f"✅ Created launcher script: {launcher_path}")
        print("💡 You can now use 'enhance <command>' from anywhere")
        
        return launcher_path

def main():
    """Main enhancement manager function"""
    parser = argparse.ArgumentParser(description="Personal Enhancement Systems Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Overview command
    overview_parser = subparsers.add_parser('overview', help='Show system overview')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a system')
    test_parser.add_argument('system', help='System ID to test')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a system')
    run_parser.add_argument('system', help='System ID to run')
    run_parser.add_argument('subcommand', nargs='?', help='System subcommand')
    
    # Help command
    help_parser = subparsers.add_parser('help', help='Show help for a system')
    help_parser.add_argument('system', help='System ID')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup launcher and aliases')
    
    args = parser.parse_args()
    
    manager = EnhancementManager()
    
    if args.command == 'overview' or not args.command:
        manager.show_system_overview()
    
    elif args.command == 'test':
        manager.test_system(args.system)
    
    elif args.command == 'run':
        manager.run_system(args.system, args.subcommand)
    
    elif args.command == 'help':
        manager.show_system_help(args.system)
    
    elif args.command == 'setup':
        print("🔧 Setting up enhancement system launcher...")
        launcher_path = manager.create_launcher_script()
        
        # Add to PATH if not already there
        bashrc_path = Path.home() / ".bashrc"
        if bashrc_path.exists():
            bashrc_content = bashrc_path.read_text()
            enhance_alias = f"export PATH=\"{Path.home()}:$PATH\""
            
            if str(Path.home()) not in bashrc_content:
                with open(bashrc_path, 'a') as f:
                    f.write(f"\n# Personal Enhancement Systems\n")
                    f.write(f"{enhance_alias}\n")
                    f.write(f"alias enhance-overview='python3 {Path.home()}/enhancement_manager.py overview'\n")
                    f.write(f"alias enhance-monitor='python3 {Path.home()}/advanced_enhancement_system.py monitor'\n")
                    f.write(f"alias enhance-report='python3 {Path.home()}/advanced_enhancement_system.py report'\n")
                
                print("✅ Added aliases to .bashrc")
                print("💡 Run 'source ~/.bashrc' or restart your terminal")
        
        print("🎉 Setup complete! You can now use:")
        print("  • enhance <command>")
        print("  • enhance-overview")
        print("  • enhance-monitor") 
        print("  • enhance-report")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()