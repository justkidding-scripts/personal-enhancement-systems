#!/usr/bin/env python3
"""
Universal Enhancement Systems Desktop Launcher
One-click installer, dependency manager, and launcher for all personal enhancement systems
"""

import os
import sys
import subprocess
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import webbrowser

class DependencyManager:
    """Manages system dependencies and installations"""
    
    def __init__(self, status_callback=None):
        self.status_callback = status_callback or print
        self.required_packages = {
            'system': ['tesseract-ocr', 'python3-tk', 'git'],
            'python': ['pytesseract', 'pillow', 'psutil']
        }
        
    def log_status(self, message: str):
        """Log status message"""
        self.status_callback(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def check_system_packages(self) -> Dict[str, bool]:
        """Check if system packages are installed"""
        status = {}
        
        for package in self.required_packages['system']:
            try:
                result = subprocess.run(
                    ['dpkg', '-l', package],
                    capture_output=True,
                    text=True
                )
                status[package] = result.returncode == 0
            except Exception:
                status[package] = False
        
        return status
    
    def check_python_packages(self) -> Dict[str, bool]:
        """Check if Python packages are installed"""
        status = {}
        
        for package in self.required_packages['python']:
            try:
                __import__(package.replace('-', '_'))
                status[package] = True
            except ImportError:
                status[package] = False
        
        return status
    
    def install_system_packages(self, packages: List[str]) -> bool:
        """Install system packages using apt"""
        self.log_status("Updating package lists...")
        
        try:
            # Update package lists
            subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
            
            # Install packages
            for package in packages:
                self.log_status(f"Installing {package}...")
                subprocess.run(
                    ['sudo', 'apt', 'install', '-y', package],
                    check=True,
                    capture_output=True
                )
            
            self.log_status("System packages installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_status(f"Error installing system packages: {e}")
            return False
    
    def install_python_packages(self, packages: List[str]) -> bool:
        """Install Python packages using pip"""
        try:
            for package in packages:
                self.log_status(f"Installing Python package {package}...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    '--user', '--break-system-packages', package
                ], check=True, capture_output=True)
            
            self.log_status("Python packages installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_status(f"Error installing Python packages: {e}")
            return False
    
    def ensure_dependencies(self) -> bool:
        """Ensure all dependencies are installed"""
        self.log_status("Checking dependencies...")
        
        # Check system packages
        system_status = self.check_system_packages()
        missing_system = [pkg for pkg, installed in system_status.items() if not installed]
        
        # Check Python packages
        python_status = self.check_python_packages()
        missing_python = [pkg for pkg, installed in python_status.items() if not installed]
        
        # Install missing packages
        if missing_system:
            self.log_status(f"Installing missing system packages: {', '.join(missing_system)}")
            if not self.install_system_packages(missing_system):
                return False
        
        if missing_python:
            self.log_status(f"Installing missing Python packages: {', '.join(missing_python)}")
            if not self.install_python_packages(missing_python):
                return False
        
        if not missing_system and not missing_python:
            self.log_status("All dependencies are already installed!")
        
        return True


class GitManager:
    """Manages Git operations for the enhancement systems"""
    
    def __init__(self, repo_path: Path, status_callback=None):
        self.repo_path = repo_path
        self.status_callback = status_callback or print
    
    def log_status(self, message: str):
        """Log status message"""
        self.status_callback(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def init_repo(self) -> bool:
        """Initialize Git repository if it doesn't exist"""
        try:
            if not (self.repo_path / '.git').exists():
                self.log_status("Initializing Git repository...")
                subprocess.run(['git', 'init'], cwd=self.repo_path, check=True, capture_output=True)
                
                # Set user config if not set
                try:
                    subprocess.run(['git', 'config', 'user.name'], 
                                 cwd=self.repo_path, check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    subprocess.run(['git', 'config', 'user.name', 'Enhancement Systems User'], 
                                 cwd=self.repo_path, check=True)
                    subprocess.run(['git', 'config', 'user.email', 'enhancement@local.dev'], 
                                 cwd=self.repo_path, check=True)
            
            return True
        except Exception as e:
            self.log_status(f"Error initializing Git repo: {e}")
            return False
    
    def create_gitignore(self):
        """Create .gitignore file"""
        gitignore_content = """# Enhancement Systems .gitignore
*.pyc
__pycache__/
*.backup
.enhancement_system.db
*.log
.DS_Store
Thumbs.db
"""
        gitignore_path = self.repo_path / '.gitignore'
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content)
            self.log_status("Created .gitignore file")
    
    def add_and_commit(self, message: str) -> bool:
        """Add all files and commit"""
        try:
            # Create .gitignore
            self.create_gitignore()
            
            # Add all files
            self.log_status("Adding files to Git...")
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'diff', '--staged', '--quiet'], 
                                  cwd=self.repo_path, capture_output=True)
            
            if result.returncode == 0:
                self.log_status("No changes to commit")
                return True
            
            # Commit changes
            self.log_status(f"Committing changes: {message}")
            subprocess.run(['git', 'commit', '-m', message], 
                         cwd=self.repo_path, check=True, capture_output=True)
            
            self.log_status("Changes committed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_status(f"Error committing changes: {e}")
            return False
    
    def setup_github_remote(self, repo_url: str) -> bool:
        """Setup GitHub remote"""
        try:
            # Check if remote already exists
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  cwd=self.repo_path, capture_output=True)
            
            if result.returncode == 0:
                self.log_status("Remote 'origin' already exists")
                return True
            
            # Add remote
            self.log_status(f"Adding remote origin: {repo_url}")
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], 
                         cwd=self.repo_path, check=True, capture_output=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_status(f"Error setting up remote: {e}")
            return False
    
    def push_to_github(self, branch: str = 'main') -> bool:
        """Push to GitHub"""
        try:
            # Set upstream and push
            self.log_status(f"Pushing to GitHub (branch: {branch})...")
            subprocess.run(['git', 'push', '-u', 'origin', branch], 
                         cwd=self.repo_path, check=True, capture_output=True)
            
            self.log_status("Successfully pushed to GitHub!")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_status(f"Error pushing to GitHub: {e}")
            return False


class EnhancementLauncherGUI:
    """Main GUI application for the Enhancement Systems Launcher"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Personal Enhancement Systems Launcher")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # System paths
        self.home_path = Path.home()
        self.systems_path = self.home_path
        
        # Managers
        self.dep_manager = DependencyManager(self.log_message)
        self.git_manager = GitManager(self.home_path, self.log_message)
        
        # Enhancement systems
        self.systems = {
            'ocr_fix': {
                'name': 'OCR Timeout Fix',
                'script': 'tesseract_timeout_fix_working.py',
                'description': 'Fix OCR timeout issues'
            },
            'ocr_integration': {
                'name': 'OCR Integration Tool',
                'script': 'integrate_ocr_timeout_fix.py',
                'description': 'Apply OCR fixes to projects'
            },
            'advanced_enhancement': {
                'name': 'Advanced Enhancement System',
                'script': 'advanced_enhancement_system.py',
                'description': 'Complete productivity framework'
            },
            'enhancement_manager': {
                'name': 'Enhancement Manager',
                'script': 'enhancement_manager.py',
                'description': 'Central control hub'
            }
        }
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="🚀 Launch")
        self.setup_main_tab(main_frame)
        
        # Dependencies tab
        deps_frame = ttk.Frame(notebook)
        notebook.add(deps_frame, text="🔧 Setup")
        self.setup_deps_tab(deps_frame)
        
        # GitHub tab
        github_frame = ttk.Frame(notebook)
        notebook.add(github_frame, text="📦 GitHub")
        self.setup_github_tab(github_frame)
        
        # Log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="📋 Logs")
        self.setup_log_tab(log_frame)
    
    def setup_main_tab(self, parent):
        """Setup main launcher tab"""
        # Title
        title_label = ttk.Label(parent, text="🚀 Personal Enhancement Systems", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to launch")
        status_label = ttk.Label(parent, textvariable=self.status_var)
        status_label.pack(pady=5)
        
        # System buttons frame
        buttons_frame = ttk.LabelFrame(parent, text="Available Systems", padding=10)
        buttons_frame.pack(fill='x', padx=20, pady=10)
        
        # Create buttons for each system
        for sys_id, sys_info in self.systems.items():
            btn_frame = ttk.Frame(buttons_frame)
            btn_frame.pack(fill='x', pady=5)
            
            # System button
            btn = ttk.Button(btn_frame, text=f"Launch {sys_info['name']}", 
                           command=lambda s=sys_id: self.launch_system(s))
            btn.pack(side='left', padx=5)
            
            # Description label
            desc_label = ttk.Label(btn_frame, text=sys_info['description'], 
                                 foreground='gray')
            desc_label.pack(side='left', padx=10)
        
        # Quick actions frame
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding=10)
        actions_frame.pack(fill='x', padx=20, pady=10)
        
        # Quick action buttons
        quick_buttons = [
            ("📊 Analyze Opportunities", self.launch_analyze),
            ("🔍 Start Monitoring", self.launch_monitor),
            ("📄 Generate Report", self.launch_report),
            ("🧪 Test OCR", self.test_ocr),
        ]
        
        for i, (text, command) in enumerate(quick_buttons):
            if i % 2 == 0:
                row_frame = ttk.Frame(actions_frame)
                row_frame.pack(fill='x', pady=2)
            
            btn = ttk.Button(row_frame, text=text, command=command)
            btn.pack(side='left', padx=5, fill='x', expand=True)
    
    def setup_deps_tab(self, parent):
        """Setup dependencies tab"""
        # Title
        title_label = ttk.Label(parent, text="🔧 System Setup & Dependencies", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Check dependencies button
        check_btn = ttk.Button(parent, text="🔍 Check Dependencies", 
                              command=self.check_dependencies)
        check_btn.pack(pady=10)
        
        # Install dependencies button
        install_btn = ttk.Button(parent, text="📦 Install All Dependencies", 
                                command=self.install_dependencies)
        install_btn.pack(pady=5)
        
        # Dependencies status frame
        self.deps_frame = ttk.LabelFrame(parent, text="Dependency Status", padding=10)
        self.deps_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill='x', padx=20, pady=10)
    
    def setup_github_tab(self, parent):
        """Setup GitHub tab"""
        # Title
        title_label = ttk.Label(parent, text="📦 GitHub Integration", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Repository URL frame
        url_frame = ttk.LabelFrame(parent, text="GitHub Repository", padding=10)
        url_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(url_frame, text="Repository URL:").pack(anchor='w')
        self.repo_url_var = tk.StringVar(value="https://github.com/username/enhancement-systems.git")
        repo_entry = ttk.Entry(url_frame, textvariable=self.repo_url_var, width=60)
        repo_entry.pack(fill='x', pady=5)
        
        # GitHub actions frame
        github_actions_frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        github_actions_frame.pack(fill='x', padx=20, pady=10)
        
        # GitHub buttons
        github_buttons = [
            ("🔄 Initialize Repository", self.init_git_repo),
            ("💾 Commit Changes", self.commit_changes),
            ("🚀 Push to GitHub", self.push_to_github),
            ("🌐 Create GitHub Repository", self.create_github_repo),
        ]
        
        for text, command in github_buttons:
            btn = ttk.Button(github_actions_frame, text=text, command=command)
            btn.pack(pady=2, fill='x')
        
        # GitHub status
        self.github_status_var = tk.StringVar(value="Repository not initialized")
        status_label = ttk.Label(parent, textvariable=self.github_status_var, 
                               foreground='blue')
        status_label.pack(pady=10)
    
    def setup_log_tab(self, parent):
        """Setup log tab"""
        # Title
        title_label = ttk.Label(parent, text="📋 System Logs", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(parent, width=80, height=25, 
                                                 wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Clear log button
        clear_btn = ttk.Button(parent, text="🗑️ Clear Logs", 
                              command=self.clear_logs)
        clear_btn.pack(pady=5)
    
    def log_message(self, message: str):
        """Log message to GUI"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
        
        # Also print to console
        print(log_entry.strip())
    
    def clear_logs(self):
        """Clear log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def check_dependencies(self):
        """Check all dependencies"""
        def check_thread():
            self.log_message("Checking system dependencies...")
            system_status = self.dep_manager.check_system_packages()
            
            self.log_message("Checking Python dependencies...")
            python_status = self.dep_manager.check_python_packages()
            
            # Update GUI with results
            self.root.after(0, self.update_deps_display, system_status, python_status)
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def update_deps_display(self, system_status: Dict, python_status: Dict):
        """Update dependencies display"""
        # Clear existing widgets
        for widget in self.deps_frame.winfo_children():
            widget.destroy()
        
        # System packages
        sys_frame = ttk.LabelFrame(self.deps_frame, text="System Packages", padding=5)
        sys_frame.pack(fill='x', pady=5)
        
        for package, installed in system_status.items():
            status_text = "✅ Installed" if installed else "❌ Missing"
            color = "green" if installed else "red"
            
            pkg_frame = ttk.Frame(sys_frame)
            pkg_frame.pack(fill='x')
            
            ttk.Label(pkg_frame, text=package).pack(side='left')
            ttk.Label(pkg_frame, text=status_text, foreground=color).pack(side='right')
        
        # Python packages
        py_frame = ttk.LabelFrame(self.deps_frame, text="Python Packages", padding=5)
        py_frame.pack(fill='x', pady=5)
        
        for package, installed in python_status.items():
            status_text = "✅ Installed" if installed else "❌ Missing"
            color = "green" if installed else "red"
            
            pkg_frame = ttk.Frame(py_frame)
            pkg_frame.pack(fill='x')
            
            ttk.Label(pkg_frame, text=package).pack(side='left')
            ttk.Label(pkg_frame, text=status_text, foreground=color).pack(side='right')
    
    def install_dependencies(self):
        """Install all dependencies"""
        def install_thread():
            self.progress_var.set(10)
            success = self.dep_manager.ensure_dependencies()
            self.progress_var.set(100)
            
            if success:
                self.log_message("✅ All dependencies installed successfully!")
                messagebox.showinfo("Success", "All dependencies installed successfully!")
            else:
                self.log_message("❌ Error installing some dependencies")
                messagebox.showerror("Error", "Failed to install some dependencies. Check logs for details.")
            
            # Refresh dependency status
            self.root.after(1000, self.check_dependencies)
        
        threading.Thread(target=install_thread, daemon=True).start()
    
    def launch_system(self, system_id: str):
        """Launch a specific system"""
        if system_id not in self.systems:
            self.log_message(f"❌ Unknown system: {system_id}")
            return
        
        sys_info = self.systems[system_id]
        script_path = self.systems_path / sys_info['script']
        
        if not script_path.exists():
            self.log_message(f"❌ Script not found: {script_path}")
            messagebox.showerror("Error", f"Script not found: {sys_info['script']}")
            return
        
        self.log_message(f"🚀 Launching {sys_info['name']}...")
        
        try:
            subprocess.Popen([sys.executable, str(script_path)], cwd=self.systems_path)
            self.status_var.set(f"Launched {sys_info['name']}")
        except Exception as e:
            self.log_message(f"❌ Error launching {sys_info['name']}: {e}")
            messagebox.showerror("Error", f"Failed to launch {sys_info['name']}: {e}")
    
    def launch_analyze(self):
        """Launch analysis"""
        self.run_enhancement_command('analyze')
    
    def launch_monitor(self):
        """Launch monitoring"""
        self.run_enhancement_command('monitor')
    
    def launch_report(self):
        """Launch report generation"""
        self.run_enhancement_command('report')
    
    def test_ocr(self):
        """Test OCR functionality"""
        self.run_enhancement_command('test-ocr')
    
    def run_enhancement_command(self, command: str):
        """Run enhancement system command"""
        script_path = self.systems_path / 'advanced_enhancement_system.py'
        
        if not script_path.exists():
            messagebox.showerror("Error", "Advanced Enhancement System not found!")
            return
        
        self.log_message(f"🚀 Running command: {command}")
        
        try:
            subprocess.Popen([sys.executable, str(script_path), command], cwd=self.systems_path)
            self.status_var.set(f"Running {command}")
        except Exception as e:
            self.log_message(f"❌ Error running {command}: {e}")
    
    def init_git_repo(self):
        """Initialize Git repository"""
        def init_thread():
            success = self.git_manager.init_repo()
            if success:
                self.root.after(0, lambda: self.github_status_var.set("Repository initialized"))
                self.log_message("✅ Git repository initialized")
            else:
                self.log_message("❌ Failed to initialize Git repository")
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def commit_changes(self):
        """Commit changes to Git"""
        def commit_thread():
            message = f"Enhancement Systems update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            success = self.git_manager.add_and_commit(message)
            if success:
                self.log_message("✅ Changes committed to Git")
            else:
                self.log_message("❌ Failed to commit changes")
        
        threading.Thread(target=commit_thread, daemon=True).start()
    
    def push_to_github(self):
        """Push to GitHub"""
        def push_thread():
            repo_url = self.repo_url_var.get().strip()
            if not repo_url:
                self.log_message("❌ Please enter a GitHub repository URL")
                return
            
            # Setup remote
            self.git_manager.setup_github_remote(repo_url)
            
            # Push to GitHub
            success = self.git_manager.push_to_github()
            if success:
                self.root.after(0, lambda: self.github_status_var.set("Successfully pushed to GitHub!"))
                self.log_message("✅ Successfully pushed to GitHub!")
            else:
                self.log_message("❌ Failed to push to GitHub")
        
        threading.Thread(target=push_thread, daemon=True).start()
    
    def create_github_repo(self):
        """Open GitHub to create new repository"""
        webbrowser.open("https://github.com/new")
        self.log_message("🌐 Opened GitHub to create new repository")
    
    def run(self):
        """Run the GUI application"""
        # Initial setup
        self.log_message("🚀 Enhancement Systems Launcher started")
        self.log_message("💡 Use the Setup tab to install dependencies")
        self.log_message("💡 Use the GitHub tab to push systems to GitHub")
        
        # Start the GUI
        self.root.mainloop()


def create_desktop_shortcut():
    """Create desktop shortcut for the launcher"""
    desktop_path = Path.home() / "Desktop"
    shortcut_path = desktop_path / "Enhancement_Systems_Launcher.desktop"
    
    launcher_script = Path(__file__)
    
    shortcut_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Enhancement Systems Launcher
Comment=Personal Enhancement Systems - One-click installer and launcher
Icon=applications-system
Exec=python3 "{launcher_script}"
Path={launcher_script.parent}
Terminal=false
Categories=Development;System;Utility;
"""
    
    shortcut_path.write_text(shortcut_content)
    shortcut_path.chmod(0o755)
    
    print(f"✅ Created desktop shortcut: {shortcut_path}")


def main():
    """Main function"""
    # Check if running from desktop (create shortcut if needed)
    if len(sys.argv) > 1 and sys.argv[1] == '--create-shortcut':
        create_desktop_shortcut()
        return
    
    # Create and run GUI
    app = EnhancementLauncherGUI()
    app.run()


if __name__ == "__main__":
    main()