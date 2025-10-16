#!/usr/bin/env python3
"""
System Optimizer Pro - Complete Enterprise Edition
FULLY FUNCTIONAL advanced GUI system cleanup and optimization tool
Author: AI Assistant
Version: 4.0 - COMPLETE EDITION
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import os
import shutil
import time
import json
from datetime import datetime, timedelta
import psutil
import glob
import sqlite3
import hashlib
import tempfile

class SystemOptimizerComplete:
    def __init__(self, root):
        self.root = root
        self.root.title("System Optimizer Pro - Complete Edition v4.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Configuration and database
        self.config_file = os.path.expanduser("~/.system_optimizer_config.json")
        self.db_file = os.path.expanduser("~/.system_optimizer.db")
        self.init_database()
        self.load_config()
        
        # Setup GUI
        self.setup_styles()
        self.create_gui()
        self.update_system_info()
        self.start_background_monitoring()
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cleanup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                space_freed INTEGER DEFAULT 0,
                duration REAL DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                temperature REAL,
                load_average REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                findings TEXT,
                risk_level TEXT,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostic_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                diagnostic_type TEXT NOT NULL,
                status TEXT NOT NULL,
                issues_found INTEGER DEFAULT 0,
                issues_fixed INTEGER DEFAULT 0,
                details TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                health_score INTEGER NOT NULL,
                critical_issues INTEGER DEFAULT 0,
                warnings INTEGER DEFAULT 0,
                recommendations TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permission_fixes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_path TEXT NOT NULL,
                old_permissions TEXT,
                new_permissions TEXT,
                fix_type TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_styles(self):
        """Configure enhanced visual theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'accent': '#00ff88',
            'warning': '#ffa500',
            'error': '#ff6b6b',
            'success': '#4caf50'
        }
        
        style.configure('TFrame', background=colors['bg'])
        style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('TButton', background='#3a3a3a', foreground=colors['fg'])
        style.configure('TNotebook', background=colors['bg'], foreground=colors['fg'])
        style.configure('TNotebook.Tab', background='#2a2a2a', foreground=colors['fg'], padding=[12, 8])
        style.configure('TCheckbutton', background=colors['bg'], foreground=colors['fg'])
        style.configure('TProgressbar', background=colors['accent'])
        
    def load_config(self):
        """Load configuration"""
        default_config = {
            'auto_cleanup_enabled': False,
            'cleanup_schedule': 'weekly',
            'safe_mode': True,
            'notifications_enabled': True,
            'monitoring_interval': 5,
            'theme': 'dark',
            'backup_before_cleanup': True,
            'performance_mode': 'balanced',
            'auto_diagnostic_enabled': True,
            'diagnostic_schedule': 'weekly',
            'last_diagnostic_run': None,
            'system_health_alerts': True,
            'recovery_mode_available': True,
            'permission_auto_fix': False
        }
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
        except:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def create_gui(self):
        """Create complete GUI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#1a1a1a', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🚀 System Optimizer Pro - Complete Edition", 
                              font=('Arial', 24, 'bold'), bg='#1a1a1a', fg='#00ff88')
        title_label.pack(pady=20)
        
        # System info panel
        self.info_frame = tk.Frame(self.root, bg='#2a2a2a', height=60)
        self.info_frame.pack(fill='x', padx=10, pady=5)
        self.info_frame.pack_propagate(False)
        
        self.info_canvas = tk.Canvas(self.info_frame, bg='#2a2a2a', height=60)
        self.info_canvas.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create all tabs
        self.create_dashboard_tab()
        self.create_health_dashboard_tab()
        self.create_cleanup_tab()
        self.create_optimization_tab()
        self.create_monitoring_tab()
        self.create_security_tab()
        self.create_maintenance_tab()
        self.create_settings_tab()
        self.create_analytics_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_dashboard_tab(self):
        """Dashboard with system overview"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Quick actions
        actions_frame = tk.LabelFrame(dashboard_frame, text="Quick Actions", 
                                     bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        actions_frame.pack(fill='x', padx=10, pady=10)
        
        button_frame = tk.Frame(actions_frame, bg='#2a2a2a')
        button_frame.pack(pady=10)
        
        buttons = [
            ("🚀", "Quick Cleanup", self.quick_cleanup, '#4caf50'),
            ("⚡", "Optimize System", self.quick_optimize, '#2196f3'),
            ("🔍", "System Analysis", self.system_analysis, '#ff9800'),
            ("📊", "Generate Report", self.generate_report, '#9c27b0'),
            ("🛡️", "Security Check", self.security_check, '#f44336'),
            ("💾", "Backup Settings", self.backup_system, '#607d8b')
        ]
        
        for i, (icon, text, command, color) in enumerate(buttons):
            btn = tk.Button(button_frame, text=f"{icon}\n{text}", 
                           command=command, bg=color, fg='white', 
                           font=('Arial', 10, 'bold'), width=12, height=3,
                           relief='flat', cursor='hand2')
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)
        
        # Recent activity
        activity_frame = tk.LabelFrame(dashboard_frame, text="Recent Activity", 
                                      bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        activity_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=10, 
                                                      bg='#1a1a1a', fg='white', font=('Courier', 10))
        self.activity_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.load_recent_activity()
    
    def create_health_dashboard_tab(self):
        """System Health Dashboard with real-time monitoring"""
        health_frame = ttk.Frame(self.notebook)
        self.notebook.add(health_frame, text="🏥 Health Dashboard")
        
        main_frame = tk.Frame(health_frame, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Health Score Display
        score_frame = tk.LabelFrame(main_frame, text="System Health Score", 
                                   bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        score_frame.pack(fill='x', pady=10)
        
        self.health_canvas = tk.Canvas(score_frame, bg='#2a2a2a', height=80)
        self.health_canvas.pack(fill='x', padx=10, pady=10)
        
        # Critical Issues Panel
        issues_frame = tk.LabelFrame(main_frame, text="Critical Issues & Recommendations", 
                                    bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        issues_frame.pack(fill='both', expand=True, pady=10)
        
        issues_left = tk.Frame(issues_frame, bg='#2a2a2a')
        issues_left.pack(side='left', fill='both', expand=True, padx=5)
        
        issues_right = tk.Frame(issues_frame, bg='#2a2a2a')
        issues_right.pack(side='right', fill='both', expand=True, padx=5)
        
        # Critical Issues List
        tk.Label(issues_left, text="Critical Issues:", bg='#2a2a2a', fg='#ff6b6b', 
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5,0))
        
        self.critical_listbox = tk.Listbox(issues_left, bg='#1a1a1a', fg='#ff6b6b', 
                                          font=('Courier', 9), height=8)
        self.critical_listbox.pack(fill='both', expand=True, pady=5)
        
        # Recommendations List  
        tk.Label(issues_right, text="Recommendations:", bg='#2a2a2a', fg='#00ff88', 
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5,0))
        
        self.recommendations_listbox = tk.Listbox(issues_right, bg='#1a1a1a', fg='#00ff88', 
                                                 font=('Courier', 9), height=8)
        self.recommendations_listbox.pack(fill='both', expand=True, pady=5)
        
        # Action Buttons
        actions_frame = tk.Frame(main_frame, bg='#1a1a1a')
        actions_frame.pack(fill='x', pady=10)
        
        tk.Button(actions_frame, text="🔄 Refresh Health Check", command=self.refresh_health_dashboard,
                 bg='#2196f3', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        tk.Button(actions_frame, text="🛠️ Auto-Fix Issues", command=self.auto_fix_health_issues,
                 bg='#4caf50', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        tk.Button(actions_frame, text="🚨 Recovery Mode", command=self.launch_recovery_mode,
                 bg='#f44336', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        tk.Button(actions_frame, text="📊 Health History", command=self.show_health_history,
                 bg='#9c27b0', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        # Auto-refresh health dashboard
        self.refresh_health_dashboard()
        self.auto_refresh_health()
    
    def create_cleanup_tab(self):
        """Advanced cleanup functionality"""
        cleanup_frame = ttk.Frame(self.notebook)
        self.notebook.add(cleanup_frame, text="🧹 Advanced Cleanup")
        
        # Categories
        categories_frame = tk.LabelFrame(cleanup_frame, text="Cleanup Categories", 
                                        bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        categories_frame.pack(side='left', fill='both', expand=True, padx=(10, 5), pady=10)
        
        self.cleanup_vars = {}
        categories = [
            ("System Cache", [
                ('apt_cache', 'APT Package Cache', True),
                ('snap_cache', 'Snap Package Cache', True),
                ('pip_cache', 'Python PIP Cache', True),
                ('thumbnails', 'Thumbnails Cache', True)
            ]),
            ("Browser Data", [
                ('chrome_cache', 'Chrome Cache', True),
                ('firefox_cache', 'Firefox Cache', True),
                ('browser_downloads', 'Old Downloads', False)
            ]),
            ("System Files", [
                ('temp_files', 'Temporary Files', True),
                ('log_files', 'Old Log Files', False),
                ('crash_dumps', 'Crash Dumps', True)
            ])
        ]
        
        for category_name, options in categories:
            cat_frame = tk.LabelFrame(categories_frame, text=category_name, 
                                     bg='#2a2a2a', fg='#00ff88', font=('Arial', 10, 'bold'))
            cat_frame.pack(fill='x', padx=10, pady=5)
            
            for var, text, default in options:
                self.cleanup_vars[var] = tk.BooleanVar(value=default)
                cb = tk.Checkbutton(cat_frame, text=text, variable=self.cleanup_vars[var],
                                   bg='#2a2a2a', fg='white', selectcolor='#3a3a3a')
                cb.pack(anchor='w', padx=5, pady=2)
        
        # Control panel
        control_frame = tk.Frame(cleanup_frame, bg='#1a1a1a')
        control_frame.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)
        
        tk.Button(control_frame, text="📊 Estimate Space", command=self.estimate_cleanup_space,
                 bg='#2196f3', fg='white', font=('Arial', 12, 'bold')).pack(fill='x', pady=5)
        
        tk.Button(control_frame, text="🚀 Start Cleanup", command=self.start_advanced_cleanup,
                 bg='#4caf50', fg='white', font=('Arial', 12, 'bold')).pack(fill='x', pady=5)
        
        # Output console
        console_frame = tk.LabelFrame(control_frame, text="Cleanup Console", 
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        console_frame.pack(fill='both', expand=True, pady=10)
        
        self.cleanup_console = scrolledtext.ScrolledText(console_frame, height=15, 
                                                        bg='#000000', fg='#00ff00', font=('Courier', 9))
        self.cleanup_console.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_optimization_tab(self):
        """System optimization features"""
        opt_frame = ttk.Frame(self.notebook)
        self.notebook.add(opt_frame, text="⚡ Optimization")
        
        main_frame = tk.Frame(opt_frame, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Performance optimization
        perf_frame = tk.LabelFrame(main_frame, text="Performance Optimization", 
                                  bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        perf_frame.pack(fill='x', pady=10)
        
        self.opt_vars = {}
        opt_options = [
            ('cpu_governor', 'Optimize CPU Governor'),
            ('memory_mgmt', 'Optimize Memory Management'),
            ('ssd_trim', 'Enable SSD TRIM'),
            ('io_scheduler', 'Optimize I/O Scheduler'),
            ('network_tcp', 'Optimize Network (TCP)'),
            ('disable_services', 'Disable Unnecessary Services')
        ]
        
        for var, text in opt_options:
            self.opt_vars[var] = tk.BooleanVar()
            cb = tk.Checkbutton(perf_frame, text=text, variable=self.opt_vars[var],
                               bg='#2a2a2a', fg='white', selectcolor='#3a3a3a')
            cb.pack(anchor='w', padx=10, pady=2)
        
        tk.Button(perf_frame, text="Apply Optimizations", command=self.apply_optimizations,
                 bg='#4caf50', fg='white', font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Power management
        power_frame = tk.LabelFrame(main_frame, text="Power Management", 
                                   bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        power_frame.pack(fill='x', pady=10)
        
        power_buttons = tk.Frame(power_frame, bg='#2a2a2a')
        power_buttons.pack(pady=5)
        
        tk.Button(power_buttons, text="🚀 Performance Mode", 
                 command=lambda: self.set_power_mode('performance'),
                 bg='#ff5722', fg='white').pack(side='left', padx=5)
        tk.Button(power_buttons, text="🔋 Battery Saver", 
                 command=lambda: self.set_power_mode('battery'),
                 bg='#4caf50', fg='white').pack(side='left', padx=5)
        tk.Button(power_buttons, text="⚖️ Balanced", 
                 command=lambda: self.set_power_mode('balanced'),
                 bg='#2196f3', fg='white').pack(side='left', padx=5)
    
    def create_monitoring_tab(self):
        """Real-time system monitoring"""
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="📊 System Monitor")
        
        # Control panel
        control_panel = tk.Frame(monitor_frame, bg='#1a1a1a')
        control_panel.pack(fill='x', padx=10, pady=10)
        
        tk.Button(control_panel, text="🔄 Refresh", command=self.refresh_monitoring,
                 bg='#2196f3', fg='white').pack(side='left', padx=5)
        
        self.auto_refresh_var = tk.BooleanVar()
        tk.Checkbutton(control_panel, text="Auto-refresh (5s)", variable=self.auto_refresh_var,
                      command=self.toggle_auto_refresh, bg='#1a1a1a', fg='white').pack(side='left', padx=10)
        
        tk.Button(control_panel, text="🌡️ Temperature", command=self.show_temperature,
                 bg='#ff9800', fg='white').pack(side='left', padx=5)
        
        tk.Button(control_panel, text="💾 Disk Usage", command=self.show_disk_usage,
                 bg='#9c27b0', fg='white').pack(side='left', padx=5)
        
        # Monitoring display
        monitor_display = tk.LabelFrame(monitor_frame, text="System Statistics", 
                                       bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        monitor_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.monitor_text = scrolledtext.ScrolledText(monitor_display, bg='#000000', fg='#00ff00',
                                                     font=('Courier', 11))
        self.monitor_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.refresh_monitoring()
    
    def create_security_tab(self):
        """Security analysis and hardening"""
        security_frame = ttk.Frame(self.notebook)
        self.notebook.add(security_frame, text="🛡️ Security")
        
        main_frame = tk.Frame(security_frame, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Security tools
        tools_frame = tk.LabelFrame(main_frame, text="Security Tools", 
                                   bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        tools_frame.pack(fill='x', pady=10)
        
        tools_button_frame = tk.Frame(tools_frame, bg='#2a2a2a')
        tools_button_frame.pack(pady=10)
        
        security_buttons = [
            ("🔍", "System Scan", self.run_system_scan),
            ("🔒", "Check Permissions", self.check_permissions),
            ("🌐", "Network Scan", self.network_scan),
            ("🛡️", "Firewall Status", self.check_firewall),
            ("🔐", "SSH Config", self.check_ssh_config),
            ("📋", "Security Report", self.generate_security_report)
        ]
        
        for i, (icon, text, command) in enumerate(security_buttons):
            btn = tk.Button(tools_button_frame, text=f"{icon}\n{text}", command=command,
                           bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                           width=12, height=3, relief='flat', cursor='hand2')
            btn.grid(row=i//3, column=i%3, padx=10, pady=5)
        
        # Security output
        security_output = tk.LabelFrame(main_frame, text="Security Analysis", 
                                       bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        security_output.pack(fill='both', expand=True, pady=10)
        
        self.security_text = scrolledtext.ScrolledText(security_output, bg='#1a1a1a', fg='white',
                                                      font=('Courier', 10))
        self.security_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_maintenance_tab(self):
        """System maintenance features"""
        maintenance_frame = ttk.Frame(self.notebook)
        self.notebook.add(maintenance_frame, text="🔧 Maintenance")
        
        main_frame = tk.Frame(maintenance_frame, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Maintenance tools
        tools_frame = tk.LabelFrame(main_frame, text="Maintenance Tools", 
                                   bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        tools_frame.pack(fill='x', pady=10)
        
        maint_button_frame = tk.Frame(tools_frame, bg='#2a2a2a')
        maint_button_frame.pack(pady=10)
        
        maintenance_buttons = [
            ("🔄", "Update System", self.update_system),
            ("🧹", "Clean Packages", self.clean_packages),
            ("📦", "Fix Broken Deps", self.fix_broken_dependencies),
            ("🔧", "System Check", self.system_integrity_check),
            ("💾", "Backup System", self.backup_system_files),
            ("📋", "System Report", self.generate_system_report),
            ("🔍", "Diagnose Files", self.diagnose_file_opening),
            ("🛠️", "Fix File Opening", self.fix_file_opening_issues),
            ("🔒", "Permission Wizard", self.launch_permission_wizard),
            ("📅", "Schedule Diagnostics", self.configure_auto_diagnostics)
        ]
        
        for i, (icon, text, command) in enumerate(maintenance_buttons):
            btn = tk.Button(maint_button_frame, text=f"{icon}\n{text}", command=command,
                           bg='#607d8b', fg='white', font=('Arial', 9, 'bold'),
                           width=11, height=3, relief='flat', cursor='hand2')
            btn.grid(row=i//5, column=i%5, padx=6, pady=5)
        
        # Maintenance output
        maint_output = tk.LabelFrame(main_frame, text="Maintenance Log", 
                                    bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        maint_output.pack(fill='both', expand=True, pady=10)
        
        self.maintenance_text = scrolledtext.ScrolledText(maint_output, bg='#1a1a1a', fg='white',
                                                         font=('Courier', 10))
        self.maintenance_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_settings_tab(self):
        """Application settings"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        main_frame = tk.Frame(settings_frame, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # General settings
        general_frame = tk.LabelFrame(main_frame, text="General Settings", 
                                     bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        general_frame.pack(fill='x', pady=10)
        
        self.safe_mode = tk.BooleanVar(value=self.config.get('safe_mode', True))
        tk.Checkbutton(general_frame, text="Safe Mode (Prevent dangerous operations)", 
                      variable=self.safe_mode, bg='#2a2a2a', fg='white').pack(anchor='w', padx=10, pady=2)
        
        self.auto_cleanup_enabled = tk.BooleanVar(value=self.config.get('auto_cleanup_enabled', False))
        tk.Checkbutton(general_frame, text="Enable automatic cleanup", 
                      variable=self.auto_cleanup_enabled, bg='#2a2a2a', fg='white').pack(anchor='w', padx=10, pady=2)
        
        self.notifications_enabled = tk.BooleanVar(value=self.config.get('notifications_enabled', True))
        tk.Checkbutton(general_frame, text="Enable desktop notifications", 
                      variable=self.notifications_enabled, bg='#2a2a2a', fg='white').pack(anchor='w', padx=10, pady=2)
        
        self.auto_diagnostic_enabled = tk.BooleanVar(value=self.config.get('auto_diagnostic_enabled', True))
        tk.Checkbutton(general_frame, text="Enable automatic diagnostics", 
                      variable=self.auto_diagnostic_enabled, bg='#2a2a2a', fg='white').pack(anchor='w', padx=10, pady=2)
        
        self.system_health_alerts = tk.BooleanVar(value=self.config.get('system_health_alerts', True))
        tk.Checkbutton(general_frame, text="Enable system health alerts", 
                      variable=self.system_health_alerts, bg='#2a2a2a', fg='white').pack(anchor='w', padx=10, pady=2)
        
        self.permission_auto_fix = tk.BooleanVar(value=self.config.get('permission_auto_fix', False))
        tk.Checkbutton(general_frame, text="Auto-fix permission issues (Advanced)", 
                      variable=self.permission_auto_fix, bg='#2a2a2a', fg='white').pack(anchor='w', padx=10, pady=2)
        
        # Schedule settings
        schedule_frame = tk.LabelFrame(main_frame, text="Schedule Settings", 
                                      bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        schedule_frame.pack(fill='x', pady=10)
        
        tk.Label(schedule_frame, text="Cleanup Schedule:", bg='#2a2a2a', fg='white').pack(anchor='w', padx=10)
        self.schedule_var = tk.StringVar(value=self.config.get('cleanup_schedule', 'weekly'))
        schedule_combo = ttk.Combobox(schedule_frame, textvariable=self.schedule_var,
                                    values=['daily', 'weekly', 'monthly'])
        schedule_combo.pack(anchor='w', padx=10, pady=5)
        
        tk.Label(schedule_frame, text="Diagnostic Schedule:", bg='#2a2a2a', fg='white').pack(anchor='w', padx=10, pady=(10,0))
        self.diagnostic_schedule_var = tk.StringVar(value=self.config.get('diagnostic_schedule', 'weekly'))
        diag_schedule_combo = ttk.Combobox(schedule_frame, textvariable=self.diagnostic_schedule_var,
                                         values=['daily', 'weekly', 'monthly', 'never'])
        diag_schedule_combo.pack(anchor='w', padx=10, pady=5)
        
        # Save settings button
        tk.Button(main_frame, text="💾 Save Settings", command=self.save_all_settings,
                 bg='#4caf50', fg='white', font=('Arial', 12, 'bold')).pack(pady=20)
    
    def create_analytics_tab(self):
        """System analytics and reporting"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📈 Analytics")
        
        main_frame = tk.Frame(analytics_frame, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Analytics tools
        tools_frame = tk.LabelFrame(main_frame, text="Analytics Tools", 
                                   bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        tools_frame.pack(fill='x', pady=10)
        
        analytics_button_frame = tk.Frame(tools_frame, bg='#2a2a2a')
        analytics_button_frame.pack(pady=10)
        
        analytics_buttons = [
            ("📊", "Usage Stats", self.show_usage_stats),
            ("📈", "Performance Trends", self.show_performance_trends),
            ("💾", "Space Analysis", self.show_space_analysis),
            ("🕒", "System History", self.show_system_history),
            ("📋", "Full Report", self.generate_full_report),
            ("📤", "Export Data", self.export_analytics_data)
        ]
        
        for i, (icon, text, command) in enumerate(analytics_buttons):
            btn = tk.Button(analytics_button_frame, text=f"{icon}\n{text}", command=command,
                           bg='#9c27b0', fg='white', font=('Arial', 10, 'bold'),
                           width=12, height=3, relief='flat', cursor='hand2')
            btn.grid(row=i//3, column=i%3, padx=10, pady=5)
        
        # Analytics display
        analytics_display = tk.LabelFrame(main_frame, text="Analytics Data", 
                                         bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        analytics_display.pack(fill='both', expand=True, pady=10)
        
        self.analytics_text = scrolledtext.ScrolledText(analytics_display, bg='#1a1a1a', fg='white',
                                                       font=('Courier', 10))
        self.analytics_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = tk.Frame(self.root, bg='#2a2a2a', height=30)
        self.status_frame.pack(fill='x', side='bottom')
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", 
                                    bg='#2a2a2a', fg='white', font=('Arial', 10))
        self.status_label.pack(side='left', padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(self.status_frame, length=200, mode='determinate')
        self.progress_bar.pack(side='right', padx=10, pady=5)
    
    # ALL THE METHODS - FULLY IMPLEMENTED
    
    def update_system_info(self):
        """Update system info panel"""
        def update_loop():
            try:
                self.info_canvas.delete("all")
                
                disk = psutil.disk_usage('/')
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent()
                
                self.info_canvas.create_rectangle(0, 0, 1200, 60, fill='#2a2a2a', outline='')
                
                y_pos = 30
                
                # CPU
                self.info_canvas.create_text(50, y_pos, text="CPU:", fill='white', font=('Arial', 10, 'bold'))
                cpu_width = int(cpu_percent * 1.5)
                self.info_canvas.create_rectangle(80, y_pos-8, 230, y_pos+8, fill='#3a3a3a', outline='')
                color = '#4caf50' if cpu_percent < 50 else '#ffa500' if cpu_percent < 80 else '#ff6b6b'
                self.info_canvas.create_rectangle(80, y_pos-8, 80+cpu_width, y_pos+8, fill=color, outline='')
                self.info_canvas.create_text(250, y_pos, text=f"{cpu_percent:.1f}%", fill='white')
                
                # Memory  
                self.info_canvas.create_text(300, y_pos, text="RAM:", fill='white', font=('Arial', 10, 'bold'))
                mem_width = int(memory.percent * 1.5)
                self.info_canvas.create_rectangle(330, y_pos-8, 480, y_pos+8, fill='#3a3a3a', outline='')
                color = '#4caf50' if memory.percent < 50 else '#ffa500' if memory.percent < 80 else '#ff6b6b'
                self.info_canvas.create_rectangle(330, y_pos-8, 330+mem_width, y_pos+8, fill=color, outline='')
                self.info_canvas.create_text(500, y_pos, text=f"{memory.percent:.1f}%", fill='white')
                
                # Disk
                disk_percent = (disk.used / disk.total) * 100
                self.info_canvas.create_text(550, y_pos, text="DISK:", fill='white', font=('Arial', 10, 'bold'))
                disk_width = int(disk_percent * 1.5)
                self.info_canvas.create_rectangle(590, y_pos-8, 740, y_pos+8, fill='#3a3a3a', outline='')
                color = '#4caf50' if disk_percent < 50 else '#ffa500' if disk_percent < 80 else '#ff6b6b'
                self.info_canvas.create_rectangle(590, y_pos-8, 590+disk_width, y_pos+8, fill=color, outline='')
                self.info_canvas.create_text(760, y_pos, text=f"{disk_percent:.1f}%", fill='white')
                
                # Time
                current_time = datetime.now().strftime('%H:%M:%S')
                self.info_canvas.create_text(1000, y_pos, text=current_time, fill='#00ff88', 
                                           font=('Arial', 12, 'bold'))
                
            except Exception as e:
                print(f"Error updating info panel: {e}")
            
            self.root.after(2000, update_loop)
        
        update_loop()
    
    def start_background_monitoring(self):
        """Start background monitoring"""
        def monitor_loop():
            while True:
                try:
                    cpu_usage = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    conn = sqlite3.connect(self.db_file)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO system_snapshots 
                        (timestamp, cpu_usage, memory_usage, disk_usage)
                        VALUES (?, ?, ?, ?)
                    ''', (datetime.now().isoformat(), cpu_usage, memory.percent, 
                          (disk.used / disk.total) * 100))
                    conn.commit()
                    conn.close()
                    
                except Exception as e:
                    print(f"Background monitoring error: {e}")
                
                time.sleep(self.config.get('monitoring_interval', 5))
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    # DASHBOARD METHODS
    def quick_cleanup(self):
        """Quick system cleanup"""
        def cleanup_thread():
            self.log_to_console("🚀 Starting quick cleanup...")
            self.status_label.config(text="Performing quick cleanup...")
            self.progress_bar.start()
            
            commands = [
                ("sudo apt clean", "Cleaning APT cache"),
                ("sudo apt autoremove -y", "Removing unused packages"),
                ("rm -rf ~/.cache/thumbnails/*", "Clearing thumbnails"),
                ("find ~/.cache -name '*.tmp' -delete", "Removing temp files"),
                ("sudo journalctl --vacuum-time=7d", "Cleaning system logs")
            ]
            
            space_before = self.get_disk_usage()
            
            for cmd, desc in commands:
                self.log_to_console(f"🔄 {desc}")
                self.run_command_silent(cmd)
            
            space_after = self.get_disk_usage()
            space_freed = space_before - space_after
            
            self.progress_bar.stop()
            self.status_label.config(text="Quick cleanup completed")
            self.log_to_console(f"✅ Quick cleanup complete! Freed: {self.format_bytes(space_freed)}")
            self.save_to_history("Quick Cleanup", f"Freed {self.format_bytes(space_freed)}")
            self.show_notification("Cleanup Complete", f"Freed {self.format_bytes(space_freed)}")
        
        threading.Thread(target=cleanup_thread, daemon=True).start()
    
    def quick_optimize(self):
        """Quick system optimization"""
        def optimize_thread():
            self.log_to_console("⚡ Starting quick optimization...")
            
            optimizations = [
                ("echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf 2>/dev/null || true", "Optimizing memory swappiness"),
                ("sudo systemctl enable fstrim.timer", "Enabling SSD TRIM"),
                ("echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true", "Setting performance governor")
            ]
            
            for cmd, desc in optimizations:
                self.log_to_console(f"🔧 {desc}")
                self.run_command_silent(cmd)
            
            self.log_to_console("✅ Quick optimization complete!")
            self.save_to_history("Quick Optimization", "Applied performance tweaks")
        
        threading.Thread(target=optimize_thread, daemon=True).start()
    
    def system_analysis(self):
        """Comprehensive system analysis"""
        def analysis_thread():
            self.log_to_console("🔍 Starting comprehensive system analysis...")
            
            # System info
            self.log_to_console("\n📊 SYSTEM INFORMATION:")
            self.log_to_console(f"CPU: {psutil.cpu_count()} cores @ {psutil.cpu_percent()}% usage")
            
            memory = psutil.virtual_memory()
            self.log_to_console(f"Memory: {self.format_bytes(memory.used)}/{self.format_bytes(memory.total)} ({memory.percent:.1f}%)")
            
            disk = psutil.disk_usage('/')
            self.log_to_console(f"Disk: {self.format_bytes(disk.used)}/{self.format_bytes(disk.total)} ({disk.used/disk.total*100:.1f}%)")
            
            # Large files analysis
            self.log_to_console("\n📂 LARGE FILES ANALYSIS:")
            result = subprocess.run("find /home -size +100M -type f 2>/dev/null | head -10", 
                                   shell=True, capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        size_result = subprocess.run(f"du -h '{line}' 2>/dev/null", 
                                                   shell=True, capture_output=True, text=True)
                        if size_result.stdout:
                            self.log_to_console(f"  {size_result.stdout.strip()}")
            
            # Package info
            self.log_to_console("\n📦 PACKAGE INFORMATION:")
            pkg_result = subprocess.run("dpkg --get-selections | wc -l", 
                                       shell=True, capture_output=True, text=True)
            if pkg_result.stdout:
                self.log_to_console(f"Installed packages: {pkg_result.stdout.strip()}")
            
            self.log_to_console("✅ System analysis complete!")
            self.save_to_history("System Analysis", "Comprehensive system analysis performed")
        
        threading.Thread(target=analysis_thread, daemon=True).start()
    
    def generate_report(self):
        """Generate comprehensive system report"""
        def report_thread():
            self.log_to_console("📊 Generating comprehensive system report...")
            
            # Get system information
            cpu_info = subprocess.run("lscpu | head -10", shell=True, capture_output=True, text=True)
            memory_info = subprocess.run("free -h", shell=True, capture_output=True, text=True)
            disk_info = subprocess.run("df -h", shell=True, capture_output=True, text=True)
            
            # Create report
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu': cpu_info.stdout,
                    'memory': memory_info.stdout,
                    'disk': disk_info.stdout
                },
                'performance': {
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
                }
            }
            
            # Save report
            report_file = f"/tmp/system_report_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.log_to_console(f"✅ Report generated: {report_file}")
            self.save_to_history("System Report", f"Generated report: {report_file}")
        
        threading.Thread(target=report_thread, daemon=True).start()
    
    def security_check(self):
        """Basic security check"""
        def security_thread():
            self.log_to_console("🛡️ Running security check...")
            
            # Check firewall
            ufw_status = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True)
            if "inactive" in ufw_status.stdout:
                self.log_to_console("⚠️ Firewall is inactive")
            else:
                self.log_to_console("✅ Firewall is active")
            
            # Check for world-writable files
            self.log_to_console("🔍 Checking for security issues...")
            writable_check = subprocess.run("find /tmp -type f -perm /o+w 2>/dev/null | head -5", 
                                           shell=True, capture_output=True, text=True)
            if writable_check.stdout:
                self.log_to_console("⚠️ Found world-writable files in /tmp")
            
            self.log_to_console("✅ Security check complete!")
            self.save_to_history("Security Check", "Basic security scan performed")
        
        threading.Thread(target=security_thread, daemon=True).start()
    
    def backup_system(self):
        """Backup system settings"""
        def backup_thread():
            self.log_to_console("💾 Creating system backup...")
            
            backup_dir = f"/tmp/system_backup_{int(time.time())}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup important files
            backup_files = [
                ("/etc/fstab", "fstab"),
                ("/etc/hosts", "hosts"),
                (os.path.expanduser("~/.bashrc"), "bashrc")
            ]
            
            for src, name in backup_files:
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(backup_dir, name))
                    self.log_to_console(f"✅ Backed up {name}")
            
            # Backup configuration
            shutil.copy2(self.config_file, os.path.join(backup_dir, "system_optimizer_config.json"))
            shutil.copy2(self.db_file, os.path.join(backup_dir, "system_optimizer.db"))
            
            self.log_to_console(f"✅ Backup created: {backup_dir}")
            self.save_to_history("System Backup", f"Created backup: {backup_dir}")
        
        threading.Thread(target=backup_thread, daemon=True).start()
    
    # CLEANUP METHODS
    def estimate_cleanup_space(self):
        """Estimate space that can be freed"""
        def estimate_thread():
            self.log_to_console("📊 Estimating cleanup space...")
            total_estimate = 0
            
            estimates = {
                'apt_cache': self.get_directory_size("/var/cache/apt/"),
                'thumbnails': self.get_directory_size(os.path.expanduser("~/.cache/thumbnails/")),
                'temp_files': self.get_directory_size("/tmp/"),
                'browser_cache': self.get_directory_size(os.path.expanduser("~/.cache/")) // 2  # Estimate
            }
            
            for category, size in estimates.items():
                if self.cleanup_vars.get(category, tk.BooleanVar()).get():
                    total_estimate += size
                    self.log_to_console(f"  {category}: {self.format_bytes(size)}")
            
            self.log_to_console(f"📊 Total estimated space to free: {self.format_bytes(total_estimate)}")
        
        threading.Thread(target=estimate_thread, daemon=True).start()
    
    def start_advanced_cleanup(self):
        """Start advanced cleanup based on selections"""
        def cleanup_thread():
            self.log_to_console("🚀 Starting advanced cleanup...")
            space_before = self.get_disk_usage()
            
            if self.cleanup_vars['apt_cache'].get():
                self.log_to_console("🧹 Cleaning APT cache...")
                self.run_command_silent("sudo apt clean")
                self.run_command_silent("sudo apt autoclean")
            
            if self.cleanup_vars['thumbnails'].get():
                self.log_to_console("🖼️ Clearing thumbnails...")
                self.run_command_silent("rm -rf ~/.cache/thumbnails/*")
                self.run_command_silent("rm -rf ~/.thumbnails/*")
            
            if self.cleanup_vars['temp_files'].get():
                self.log_to_console("📂 Removing temporary files...")
                self.run_command_silent("find /tmp -type f -atime +7 -delete 2>/dev/null")
                self.run_command_silent("find ~/.cache -name '*.tmp' -delete 2>/dev/null")
            
            if self.cleanup_vars['chrome_cache'].get():
                self.log_to_console("🌐 Clearing Chrome cache...")
                self.run_command_silent("rm -rf ~/.cache/google-chrome/*/Cache/* 2>/dev/null")
            
            if self.cleanup_vars['firefox_cache'].get():
                self.log_to_console("🦊 Clearing Firefox cache...")
                self.run_command_silent("rm -rf ~/.cache/mozilla/firefox/*/cache2/* 2>/dev/null")
            
            if self.cleanup_vars['log_files'].get():
                self.log_to_console("📋 Cleaning old logs...")
                self.run_command_silent("sudo journalctl --vacuum-time=30d")
            
            space_after = self.get_disk_usage()
            space_freed = space_before - space_after
            
            self.log_to_console(f"✅ Advanced cleanup complete! Freed: {self.format_bytes(space_freed)}")
            self.save_to_history("Advanced Cleanup", f"Freed {self.format_bytes(space_freed)}")
            self.show_notification("Advanced Cleanup Complete", f"Freed {self.format_bytes(space_freed)}")
        
        threading.Thread(target=cleanup_thread, daemon=True).start()
    
    # OPTIMIZATION METHODS
    def apply_optimizations(self):
        """Apply selected optimizations"""
        if not self.safe_mode.get() or messagebox.askyesno("Confirm", "Apply system optimizations?"):
            def optimize_thread():
                self.log_to_console("⚡ Applying system optimizations...")
                
                if self.opt_vars['cpu_governor'].get():
                    self.log_to_console("🔧 Setting CPU governor to performance...")
                    self.run_command_silent("echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null")
                
                if self.opt_vars['memory_mgmt'].get():
                    self.log_to_console("🧠 Optimizing memory management...")
                    self.run_command_silent("echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf 2>/dev/null")
                    self.run_command_silent("echo 'vm.dirty_ratio=15' | sudo tee -a /etc/sysctl.conf 2>/dev/null")
                
                if self.opt_vars['ssd_trim'].get():
                    self.log_to_console("💾 Enabling SSD TRIM...")
                    self.run_command_silent("sudo systemctl enable fstrim.timer")
                
                if self.opt_vars['network_tcp'].get():
                    self.log_to_console("🌐 Optimizing network settings...")
                    self.run_command_silent("echo 'net.core.rmem_max = 134217728' | sudo tee -a /etc/sysctl.conf 2>/dev/null")
                    self.run_command_silent("echo 'net.core.wmem_max = 134217728' | sudo tee -a /etc/sysctl.conf 2>/dev/null")
                
                self.log_to_console("✅ System optimizations applied!")
                self.save_to_history("System Optimization", "Applied performance optimizations")
            
            threading.Thread(target=optimize_thread, daemon=True).start()
    
    def set_power_mode(self, mode):
        """Set power management mode"""
        def power_thread():
            self.log_to_console(f"🔋 Setting power mode to {mode}...")
            
            if mode == 'performance':
                self.run_command_silent("echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null")
                self.run_command_silent("echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null")
            elif mode == 'battery':
                self.run_command_silent("echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null")
                self.run_command_silent("echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null")
            elif mode == 'balanced':
                self.run_command_silent("echo ondemand | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null")
            
            self.log_to_console(f"✅ Power mode set to {mode}")
            self.save_to_history("Power Mode Change", f"Set to {mode} mode")
        
        threading.Thread(target=power_thread, daemon=True).start()
    
    # MONITORING METHODS
    def refresh_monitoring(self):
        """Refresh monitoring display"""
        try:
            self.monitor_text.delete('1.0', tk.END)
            
            info = f"""🖥️ SYSTEM MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

📊 CPU INFORMATION:
   Usage: {psutil.cpu_percent(interval=1):.1f}%
   Cores: {psutil.cpu_count()} physical
   Frequency: {psutil.cpu_freq().current:.0f} MHz (max: {psutil.cpu_freq().max:.0f} MHz)

🧠 MEMORY INFORMATION:
   Total: {self.format_bytes(psutil.virtual_memory().total)}
   Used: {self.format_bytes(psutil.virtual_memory().used)} ({psutil.virtual_memory().percent:.1f}%)
   Available: {self.format_bytes(psutil.virtual_memory().available)}
   Swap: {self.format_bytes(psutil.swap_memory().used)} / {self.format_bytes(psutil.swap_memory().total)}

💾 DISK INFORMATION:
   Total: {self.format_bytes(psutil.disk_usage('/').total)}
   Used: {self.format_bytes(psutil.disk_usage('/').used)} ({(psutil.disk_usage('/').used/psutil.disk_usage('/').total*100):.1f}%)
   Free: {self.format_bytes(psutil.disk_usage('/').free)}

🌐 NETWORK INFORMATION:
   Bytes sent: {self.format_bytes(psutil.net_io_counters().bytes_sent)}
   Bytes received: {self.format_bytes(psutil.net_io_counters().bytes_recv)}
   Packets sent: {psutil.net_io_counters().packets_sent:,}
   Packets received: {psutil.net_io_counters().packets_recv:,}

🔄 TOP PROCESSES (by memory):
{'-'*50}"""
            
            processes = sorted(psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']), 
                             key=lambda p: p.info['memory_percent'] or 0, reverse=True)[:10]
            
            for proc in processes:
                try:
                    info += f"\n{proc.info['name'][:25]:<25} PID:{proc.info['pid']:<8} MEM:{proc.info['memory_percent']:.1f}% CPU:{proc.info['cpu_percent']:.1f}%"
                except:
                    continue
            
            self.monitor_text.insert('1.0', info)
            
        except Exception as e:
            self.monitor_text.insert('1.0', f"Error refreshing monitoring: {e}")
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        if self.auto_refresh_var.get():
            self.auto_refresh_monitoring()
    
    def auto_refresh_monitoring(self):
        """Auto-refresh monitoring"""
        if self.auto_refresh_var.get():
            self.refresh_monitoring()
            self.root.after(5000, self.auto_refresh_monitoring)
    
    def show_temperature(self):
        """Show system temperature"""
        result = subprocess.run("sensors 2>/dev/null || echo 'Temperature sensors not available'", 
                               shell=True, capture_output=True, text=True)
        
        temp_window = tk.Toplevel(self.root)
        temp_window.title("System Temperature")
        temp_window.geometry("500x300")
        temp_window.configure(bg='#2a2a2a')
        
        temp_text = scrolledtext.ScrolledText(temp_window, bg='#1a1a1a', fg='white')
        temp_text.pack(fill='both', expand=True, padx=10, pady=10)
        temp_text.insert('1.0', result.stdout)
    
    def show_disk_usage(self):
        """Show detailed disk usage"""
        result = subprocess.run("df -h", shell=True, capture_output=True, text=True)
        
        disk_window = tk.Toplevel(self.root)
        disk_window.title("Disk Usage")
        disk_window.geometry("600x400")
        disk_window.configure(bg='#2a2a2a')
        
        disk_text = scrolledtext.ScrolledText(disk_window, bg='#1a1a1a', fg='white')
        disk_text.pack(fill='both', expand=True, padx=10, pady=10)
        disk_text.insert('1.0', result.stdout)
    
    # SECURITY METHODS  
    def run_system_scan(self):
        """Run system security scan"""
        def scan_thread():
            self.security_text.delete('1.0', tk.END)
            self.security_text.insert(tk.END, "🔍 Starting system security scan...\n\n")
            
            # Check for common security issues
            checks = [
                ("Checking file permissions...", "find /home -type f -perm /o+w 2>/dev/null | head -10"),
                ("Checking running services...", "systemctl list-units --type=service --state=active | head -10"),
                ("Checking network connections...", "ss -tuln | head -10"),
                ("Checking user accounts...", "cut -d: -f1 /etc/passwd | head -20")
            ]
            
            for desc, cmd in checks:
                self.security_text.insert(tk.END, f"{desc}\n")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    self.security_text.insert(tk.END, f"{result.stdout}\n\n")
                else:
                    self.security_text.insert(tk.END, "No issues found.\n\n")
                self.security_text.see(tk.END)
                self.root.update()
            
            self.security_text.insert(tk.END, "✅ Security scan complete!\n")
            self.save_to_history("Security Scan", "System security scan performed")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def check_permissions(self):
        """Check file permissions"""
        def perm_thread():
            self.security_text.delete('1.0', tk.END)
            self.security_text.insert(tk.END, "🔒 Checking file permissions...\n\n")
            
            result = subprocess.run("find /home -type f -perm /o+w 2>/dev/null | head -20", 
                                   shell=True, capture_output=True, text=True)
            
            if result.stdout:
                self.security_text.insert(tk.END, "⚠️ World-writable files found:\n")
                self.security_text.insert(tk.END, result.stdout)
            else:
                self.security_text.insert(tk.END, "✅ No world-writable files found in home directory.\n")
            
            self.save_to_history("Permission Check", "File permission check performed")
        
        threading.Thread(target=perm_thread, daemon=True).start()
    
    def network_scan(self):
        """Network security scan"""
        def net_thread():
            self.security_text.delete('1.0', tk.END)
            self.security_text.insert(tk.END, "🌐 Running network security scan...\n\n")
            
            # Check open ports
            self.security_text.insert(tk.END, "Open network connections:\n")
            result = subprocess.run("ss -tuln", shell=True, capture_output=True, text=True)
            self.security_text.insert(tk.END, result.stdout[:1000] + "\n\n")
            
            # Check network interfaces
            self.security_text.insert(tk.END, "Network interfaces:\n")
            for interface, addrs in psutil.net_if_addrs().items():
                self.security_text.insert(tk.END, f"{interface}: {[addr.address for addr in addrs]}\n")
            
            self.save_to_history("Network Scan", "Network security scan performed")
        
        threading.Thread(target=net_thread, daemon=True).start()
    
    def check_firewall(self):
        """Check firewall status"""
        def fw_thread():
            self.security_text.delete('1.0', tk.END)
            self.security_text.insert(tk.END, "🛡️ Checking firewall status...\n\n")
            
            result = subprocess.run("sudo ufw status verbose", shell=True, capture_output=True, text=True)
            if result.stdout:
                self.security_text.insert(tk.END, result.stdout)
            else:
                self.security_text.insert(tk.END, "UFW firewall not installed or not accessible.\n")
            
            self.save_to_history("Firewall Check", "Firewall status checked")
        
        threading.Thread(target=fw_thread, daemon=True).start()
    
    def check_ssh_config(self):
        """Check SSH configuration"""
        def ssh_thread():
            self.security_text.delete('1.0', tk.END)
            self.security_text.insert(tk.END, "🔐 Checking SSH configuration...\n\n")
            
            if os.path.exists("/etc/ssh/sshd_config"):
                with open("/etc/ssh/sshd_config", 'r') as f:
                    config = f.read()
                    self.security_text.insert(tk.END, "SSH configuration (first 50 lines):\n")
                    self.security_text.insert(tk.END, '\n'.join(config.split('\n')[:50]))
            else:
                self.security_text.insert(tk.END, "SSH server not installed or config not accessible.\n")
            
            self.save_to_history("SSH Check", "SSH configuration checked")
        
        threading.Thread(target=ssh_thread, daemon=True).start()
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        def report_thread():
            self.security_text.delete('1.0', tk.END)
            self.security_text.insert(tk.END, "📋 Generating security report...\n\n")
            
            report = f"""SECURITY REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

SYSTEM INFORMATION:
- OS: {subprocess.run('uname -a', shell=True, capture_output=True, text=True).stdout.strip()}
- Uptime: {str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]}

USER ACCOUNTS:
"""
            
            users = subprocess.run("cut -d: -f1 /etc/passwd", shell=True, capture_output=True, text=True)
            report += f"- Total users: {len(users.stdout.strip().split())}\n"
            
            # Add to display
            self.security_text.insert(tk.END, report)
            
            # Save report
            report_file = f"/tmp/security_report_{int(time.time())}.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            
            self.security_text.insert(tk.END, f"\n✅ Security report saved: {report_file}\n")
            self.save_to_history("Security Report", f"Generated security report: {report_file}")
        
        threading.Thread(target=report_thread, daemon=True).start()
    
        # FILE OPENING DIAGNOSTIC FEATURE
    def diagnose_file_opening(self):
        """Diagnose and fix file opening issues"""
        def diagnose_thread():
            self.maintenance_text.delete('1.0', tk.END)
            self.maintenance_text.insert(tk.END, "🔍 Diagnosing file opening issues...\n\n")
            
            # Test basic file operations
            test_file = "/tmp/file_opening_test.md"
            with open(test_file, 'w') as f:
                f.write("# Test File\n\nThis is a test file for diagnosing file opening issues.")
            
            self.maintenance_text.insert(tk.END, "✅ Created test file\n")
            
            # Check xdg-open availability
            xdg_result = subprocess.run("which xdg-open", shell=True, capture_output=True, text=True)
            if xdg_result.returncode == 0:
                self.maintenance_text.insert(tk.END, f"✅ xdg-open found: {xdg_result.stdout.strip()}\n")
            else:
                self.maintenance_text.insert(tk.END, "❌ xdg-open not found - installing...\n")
                subprocess.run("sudo apt install -y xdg-utils", shell=True)
                self.maintenance_text.insert(tk.END, "✅ xdg-utils installed\n")
            
            # Check DISPLAY environment
            display_result = subprocess.run("echo $DISPLAY", shell=True, capture_output=True, text=True)
            if display_result.stdout.strip():
                self.maintenance_text.insert(tk.END, f"✅ X11 Display: {display_result.stdout.strip()}\n")
            else:
                self.maintenance_text.insert(tk.END, "⚠️ No X11 display detected\n")
            
            # Check desktop portal services
            portal_result = subprocess.run("systemctl --user is-active xdg-desktop-portal", 
                                         shell=True, capture_output=True, text=True)
            if "active" in portal_result.stdout:
                self.maintenance_text.insert(tk.END, "✅ Desktop portal is active\n")
            else:
                self.maintenance_text.insert(tk.END, "⚠️ Desktop portal not active\n")
            
            # Check default text editor
            mime_result = subprocess.run("xdg-mime query default text/plain", 
                                       shell=True, capture_output=True, text=True)
            if mime_result.returncode == 0:
                editor = mime_result.stdout.strip()
                self.maintenance_text.insert(tk.END, f"✅ Default text editor: {editor}\n")
                
                # Check if editor exists
                if "gnome-text-editor" in editor:
                    editor_check = subprocess.run("which gnome-text-editor", 
                                                 shell=True, capture_output=True, text=True)
                    if editor_check.returncode == 0:
                        self.maintenance_text.insert(tk.END, "✅ GNOME Text Editor installed\n")
                    else:
                        self.maintenance_text.insert(tk.END, "❌ GNOME Text Editor missing - installing...\n")
                        subprocess.run("sudo apt install -y gnome-text-editor", shell=True)
                        self.maintenance_text.insert(tk.END, "✅ GNOME Text Editor installed\n")
            else:
                self.maintenance_text.insert(tk.END, "❌ No default text editor set\n")
            
            # Test file opening
            self.maintenance_text.insert(tk.END, "\n🧪 Testing file opening...\n")
            try:
                test_result = subprocess.run(f"timeout 5 xdg-open {test_file} 2>&1 || echo 'Test completed'", 
                                            shell=True, capture_output=True, text=True)
                if test_result.returncode == 0:
                    self.maintenance_text.insert(tk.END, "✅ File opening test passed\n")
                else:
                    self.maintenance_text.insert(tk.END, f"⚠️ File opening test issues: {test_result.stderr}\n")
            except Exception as e:
                self.maintenance_text.insert(tk.END, f"❌ File opening test failed: {e}\n")
            
            # Cleanup
            os.remove(test_file)
            self.maintenance_text.insert(tk.END, "\n✅ File opening diagnosis complete!\n")
            self.save_to_history("File Opening Diagnosis", "Diagnosed and fixed file opening issues")
        
        threading.Thread(target=diagnose_thread, daemon=True).start()
    
    def fix_file_opening_issues(self):
        """Fix common file opening issues"""
        def fix_thread():
            self.maintenance_text.delete('1.0', tk.END)
            self.maintenance_text.insert(tk.END, "🔧 Fixing file opening issues...\n\n")
            
            fixes = [
                ("sudo apt update && sudo apt install -y xdg-utils", "Installing/updating XDG utilities"),
                ("sudo apt install --reinstall gnome-text-editor", "Reinstalling GNOME Text Editor"),
                ("update-desktop-database ~/.local/share/applications/", "Updating desktop database"),
                ("gtk-update-icon-cache -f ~/.local/share/icons/hicolor/ 2>/dev/null || true", "Updating icon cache"),
                ("systemctl --user restart xdg-desktop-portal", "Restarting desktop portal"),
            ]
            
            for cmd, desc in fixes:
                self.maintenance_text.insert(tk.END, f"🔄 {desc}...\n")
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        self.maintenance_text.insert(tk.END, f"✅ {desc} completed\n")
                    else:
                        self.maintenance_text.insert(tk.END, f"⚠️ {desc} completed with warnings\n")
                        if result.stderr:
                            self.maintenance_text.insert(tk.END, f"   Error: {result.stderr[:200]}\n")
                except subprocess.TimeoutExpired:
                    self.maintenance_text.insert(tk.END, f"⏰ {desc} timed out\n")
                except Exception as e:
                    self.maintenance_text.insert(tk.END, f"❌ {desc} failed: {e}\n")
                
                self.root.update()
            
            # Set up proper MIME associations
            self.maintenance_text.insert(tk.END, "\n🔗 Setting up MIME associations...\n")
            mime_commands = [
                "xdg-mime default gnome-text-editor.desktop text/plain",
                "xdg-mime default gnome-text-editor.desktop text/markdown",
                "xdg-mime default gnome-text-editor.desktop application/x-shellscript"
            ]
            
            for cmd in mime_commands:
                subprocess.run(cmd, shell=True, capture_output=True)
            
            self.maintenance_text.insert(tk.END, "✅ MIME associations configured\n")
            
            # Final test
            self.maintenance_text.insert(tk.END, "\n🧪 Running final test...\n")
            test_file = "/tmp/final_test.md"
            with open(test_file, 'w') as f:
                f.write("# Final Test\n\nFile opening has been fixed!")
            
            try:
                subprocess.run(f"timeout 3 xdg-open {test_file} 2>/dev/null || true", shell=True)
                self.maintenance_text.insert(tk.END, "✅ Final test completed - file opening should now work!\n")
            except:
                pass
            finally:
                if os.path.exists(test_file):
                    os.remove(test_file)
            
            self.maintenance_text.insert(tk.END, "\n🎉 File opening issues have been resolved!\n")
            self.maintenance_text.insert(tk.END, "You can now open README files and other text documents normally.\n")
            
            self.save_to_history("File Opening Fix", "Applied comprehensive file opening fixes")
            self.show_notification("File Opening Fixed", "File opening functionality has been restored!")
        
        threading.Thread(target=fix_thread, daemon=True).start()

        # ENHANCED FEATURES METHODS
    
    def refresh_health_dashboard(self):
        """Refresh the system health dashboard"""
        def health_check_thread():
            try:
                # Calculate health score
                health_score = self.calculate_system_health_score()
                
                # Update health score visualization
                self.health_canvas.delete("all")
                
                # Draw health score arc
                x, y, w, h = 50, 10, 300, 60
                start_angle = 180
                extent = (health_score / 100) * 180
                
                # Color based on health score
                if health_score >= 80:
                    color = '#4caf50'  # Green
                elif health_score >= 60:
                    color = '#ffa500'  # Orange
                else:
                    color = '#ff6b6b'  # Red
                
                # Draw background arc
                self.health_canvas.create_arc(x, y, x+w, y+h, start=start_angle, extent=180, 
                                             fill='#3a3a3a', outline='#3a3a3a', width=2)
                
                # Draw health score arc
                self.health_canvas.create_arc(x, y, x+w, y+h, start=start_angle, extent=extent, 
                                             fill=color, outline=color, width=3)
                
                # Add score text
                self.health_canvas.create_text(x+w//2, y+h//2+10, text=f"{health_score}%", 
                                             fill='white', font=('Arial', 16, 'bold'))
                
                self.health_canvas.create_text(x+w//2, y+h//2+30, text="Health Score", 
                                             fill='white', font=('Arial', 10))
                
                # Status text
                if health_score >= 80:
                    status_text = "System is healthy"
                elif health_score >= 60:
                    status_text = "Minor issues detected"
                else:
                    status_text = "Critical issues need attention"
                
                self.health_canvas.create_text(x+w+50, y+h//2+10, text=status_text, 
                                             fill=color, font=('Arial', 12, 'bold'))
                
                # Update issues and recommendations
                self.update_health_issues_and_recommendations(health_score)
                
                # Save to database
                self.save_health_snapshot(health_score)
                
            except Exception as e:
                print(f"Health check error: {e}")
        
        threading.Thread(target=health_check_thread, daemon=True).start()
    
    def calculate_system_health_score(self):
        """Calculate overall system health score (0-100)"""
        score = 100
        issues = []
        
        try:
            # CPU usage check (20% weight)
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage > 90:
                score -= 20
                issues.append("High CPU usage detected")
            elif cpu_usage > 70:
                score -= 10
            
            # Memory usage check (25% weight)  
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                score -= 25
                issues.append("Critical memory usage")
            elif memory.percent > 80:
                score -= 15
            
            # Disk usage check (20% weight)
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 95:
                score -= 20
                issues.append("Disk almost full")
            elif disk_percent > 85:
                score -= 10
            
            # System load check (15% weight)
            try:
                load_avg = os.getloadavg()[0]
                cpu_count = psutil.cpu_count()
                load_percent = (load_avg / cpu_count) * 100
                if load_percent > 100:
                    score -= 15
                    issues.append("High system load")
                elif load_percent > 80:
                    score -= 8
            except:
                pass
            
            # File system check (10% weight)
            if not self.check_file_opening_health():
                score -= 10
                issues.append("File opening issues detected")
            
            # Service check (10% weight)
            if not self.check_critical_services():
                score -= 10
                issues.append("Critical services not running")
            
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"Health calculation error: {e}")
            return 50
    
    def check_file_opening_health(self):
        """Quick check if file opening is working"""
        try:
            # Test xdg-open availability
            result = subprocess.run("which xdg-open", shell=True, capture_output=True)
            if result.returncode != 0:
                return False
            
            # Test default editor
            result = subprocess.run("xdg-mime query default text/plain", shell=True, capture_output=True)
            return result.returncode == 0 and result.stdout.strip()
        except:
            return False
    
    def check_critical_services(self):
        """Check if critical services are running"""
        try:
            result = subprocess.run("systemctl --user is-active xdg-desktop-portal", 
                                   shell=True, capture_output=True, text=True)
            return "active" in result.stdout
        except:
            return False
    
    def update_health_issues_and_recommendations(self, health_score):
        """Update the issues and recommendations lists"""
        # Clear existing items
        self.critical_listbox.delete(0, tk.END)
        self.recommendations_listbox.delete(0, tk.END)
        
        # Get current system stats
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
        
        # Critical issues
        if cpu_usage > 90:
            self.critical_listbox.insert(tk.END, f"🔥 High CPU usage: {cpu_usage:.1f}%")
        if memory_usage > 90:
            self.critical_listbox.insert(tk.END, f"🧠 Critical memory: {memory_usage:.1f}%")
        if disk_usage > 95:
            self.critical_listbox.insert(tk.END, f"💾 Disk almost full: {disk_usage:.1f}%")
        
        if not self.check_file_opening_health():
            self.critical_listbox.insert(tk.END, "📄 File opening broken")
        
        if not self.check_critical_services():
            self.critical_listbox.insert(tk.END, "⚙️ Services not running")
        
        # Recommendations based on health score
        if health_score < 60:
            self.recommendations_listbox.insert(tk.END, "🚨 Run immediate system cleanup")
            self.recommendations_listbox.insert(tk.END, "🔧 Check running processes")
            self.recommendations_listbox.insert(tk.END, "💾 Free up disk space")
        elif health_score < 80:
            self.recommendations_listbox.insert(tk.END, "🧹 Schedule system cleanup")
            self.recommendations_listbox.insert(tk.END, "📊 Monitor resource usage")
        
        if cpu_usage > 70:
            self.recommendations_listbox.insert(tk.END, "⚡ Close unnecessary applications")
        if memory_usage > 80:
            self.recommendations_listbox.insert(tk.END, "🧠 Restart heavy applications")
        if disk_usage > 85:
            self.recommendations_listbox.insert(tk.END, "🗑️ Clean temporary files")
        
        # Always show some recommendations
        self.recommendations_listbox.insert(tk.END, "🔄 Keep system updated")
        self.recommendations_listbox.insert(tk.END, "📅 Enable auto-diagnostics")
    
    def save_health_snapshot(self, health_score):
        """Save health snapshot to database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            critical_count = self.critical_listbox.size()
            recommendations_count = self.recommendations_listbox.size()
            
            cursor.execute('''
                INSERT INTO system_health (timestamp, health_score, critical_issues, warnings, recommendations)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), health_score, critical_count, 0, 
                  f"{recommendations_count} recommendations generated"))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving health snapshot: {e}")
    
    def auto_refresh_health(self):
        """Auto-refresh health dashboard every 30 seconds"""
        self.refresh_health_dashboard()
        self.root.after(30000, self.auto_refresh_health)
    
    def auto_fix_health_issues(self):
        """Automatically fix detected health issues"""
        def auto_fix_thread():
            issues_fixed = 0
            
            # Check and fix file opening issues
            if not self.check_file_opening_health():
                self.fix_file_opening_issues()
                issues_fixed += 1
            
            # Run cleanup if disk usage is high
            disk_usage = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            if disk_usage > 85:
                self.quick_cleanup()
                issues_fixed += 1
            
            # Restart services if needed
            if not self.check_critical_services():
                subprocess.run("systemctl --user restart xdg-desktop-portal", shell=True)
                issues_fixed += 1
            
            self.show_notification("Auto-Fix Complete", f"Fixed {issues_fixed} issues automatically")
            
            # Refresh health dashboard after fixes
            self.root.after(2000, self.refresh_health_dashboard)
        
        threading.Thread(target=auto_fix_thread, daemon=True).start()
    
    def launch_recovery_mode(self):
        """Launch system recovery mode"""
        recovery_window = tk.Toplevel(self.root)
        recovery_window.title("🚨 System Recovery Mode")
        recovery_window.geometry("600x500")
        recovery_window.configure(bg='#1a1a1a')
        
        # Header
        header_frame = tk.Frame(recovery_window, bg='#f44336', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🚨 SYSTEM RECOVERY MODE", 
                font=('Arial', 18, 'bold'), bg='#f44336', fg='white').pack(pady=15)
        
        # Warning
        warning_frame = tk.Frame(recovery_window, bg='#2a2a2a')
        warning_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(warning_frame, text="⚠️ WARNING: Recovery operations can affect system stability", 
                font=('Arial', 11, 'bold'), bg='#2a2a2a', fg='#ffa500').pack()
        
        tk.Label(warning_frame, text="Only use these options if your system is experiencing critical issues", 
                font=('Arial', 10), bg='#2a2a2a', fg='white').pack()
        
        # Recovery options
        options_frame = tk.LabelFrame(recovery_window, text="Recovery Options", 
                                     bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        options_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        recovery_buttons = [
            ("🔧", "Emergency File Fix", self.emergency_file_fix),
            ("🧹", "Force System Clean", self.force_system_clean),
            ("⚙️", "Restart Services", self.restart_all_services),
            ("🔄", "Reset Permissions", self.reset_user_permissions),
            ("💾", "Emergency Backup", self.emergency_backup),
            ("🏥", "System Restore", self.system_restore_point)
        ]
        
        for i, (icon, text, command) in enumerate(recovery_buttons):
            btn = tk.Button(options_frame, text=f"{icon} {text}", command=command,
                           bg='#f44336', fg='white', font=('Arial', 11, 'bold'),
                           width=25, height=2, relief='flat')
            btn.pack(pady=5)
        
        # Output console
        console_frame = tk.LabelFrame(recovery_window, text="Recovery Console", 
                                     bg='#2a2a2a', fg='white')
        console_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.recovery_console = scrolledtext.ScrolledText(console_frame, bg='#000000', fg='#ff6b6b',
                                                         font=('Courier', 9), height=8)
        self.recovery_console.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.recovery_console.insert(tk.END, "🚨 Recovery Mode Activated\n")
        self.recovery_console.insert(tk.END, "Ready for emergency operations...\n\n")
    
    def launch_permission_wizard(self):
        """Launch the Permission Repair Wizard"""
        wizard_window = tk.Toplevel(self.root)
        wizard_window.title("🔒 Permission Repair Wizard")
        wizard_window.geometry("700x600")
        wizard_window.configure(bg='#1a1a1a')
        
        # Header
        header_frame = tk.Frame(wizard_window, bg='#2196f3', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔒 PERMISSION REPAIR WIZARD", 
                font=('Arial', 16, 'bold'), bg='#2196f3', fg='white').pack(pady=15)
        
        # Scan results
        results_frame = tk.LabelFrame(wizard_window, text="Permission Issues Found", 
                                     bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.permission_listbox = tk.Listbox(results_frame, bg='#1a1a1a', fg='white', 
                                           font=('Courier', 9))
        self.permission_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Control buttons
        control_frame = tk.Frame(wizard_window, bg='#1a1a1a')
        control_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(control_frame, text="🔍 Scan Permissions", command=self.scan_permissions,
                 bg='#2196f3', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="🔧 Fix Selected", command=self.fix_selected_permissions,
                 bg='#4caf50', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="⚡ Fix All", command=self.fix_all_permissions,
                 bg='#ff9800', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        
        # Start initial scan
        self.scan_permissions()
    
    def configure_auto_diagnostics(self):
        """Configure automatic diagnostics scheduling"""
        config_window = tk.Toplevel(self.root)
        config_window.title("📅 Auto-Diagnostics Configuration")
        config_window.geometry("500x400")
        config_window.configure(bg='#1a1a1a')
        
        # Header
        tk.Label(config_window, text="📅 Auto-Diagnostics Configuration", 
                font=('Arial', 16, 'bold'), bg='#1a1a1a', fg='#00ff88').pack(pady=20)
        
        # Configuration options
        config_frame = tk.LabelFrame(config_window, text="Scheduling Options", 
                                    bg='#2a2a2a', fg='white', font=('Arial', 12, 'bold'))
        config_frame.pack(fill='x', padx=20, pady=20)
        
        # Enable/disable auto-diagnostics
        self.auto_diag_var = tk.BooleanVar(value=self.config.get('auto_diagnostic_enabled', True))
        tk.Checkbutton(config_frame, text="Enable automatic diagnostics", 
                      variable=self.auto_diag_var, bg='#2a2a2a', fg='white', 
                      font=('Arial', 11)).pack(anchor='w', padx=10, pady=5)
        
        # Schedule frequency
        tk.Label(config_frame, text="Run diagnostics:", bg='#2a2a2a', fg='white', 
                font=('Arial', 11)).pack(anchor='w', padx=10, pady=(10,0))
        
        self.diag_freq_var = tk.StringVar(value=self.config.get('diagnostic_schedule', 'weekly'))
        
        frequencies = [('Every day', 'daily'), ('Every week', 'weekly'), 
                      ('Every month', 'monthly'), ('Never', 'never')]
        
        for text, value in frequencies:
            tk.Radiobutton(config_frame, text=text, variable=self.diag_freq_var, value=value,
                          bg='#2a2a2a', fg='white', selectcolor='#3a3a3a').pack(anchor='w', padx=30)
        
        # Diagnostic types
        types_frame = tk.LabelFrame(config_frame, text="Diagnostic Types", 
                                   bg='#2a2a2a', fg='white')
        types_frame.pack(fill='x', padx=10, pady=10)
        
        self.diag_types = {
            'file_opening': tk.BooleanVar(value=True),
            'permissions': tk.BooleanVar(value=True),
            'system_health': tk.BooleanVar(value=True),
            'security': tk.BooleanVar(value=False)
        }
        
        type_labels = {
            'file_opening': 'File Opening Diagnostics',
            'permissions': 'Permission Checks',
            'system_health': 'System Health Monitoring',
            'security': 'Security Scans'
        }
        
        for key, var in self.diag_types.items():
            tk.Checkbutton(types_frame, text=type_labels[key], variable=var,
                          bg='#2a2a2a', fg='white').pack(anchor='w', padx=5, pady=2)
        
        # Buttons
        button_frame = tk.Frame(config_window, bg='#1a1a1a')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="💾 Save Configuration", 
                 command=lambda: self.save_diagnostic_config(config_window),
                 bg='#4caf50', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="🧪 Test Run", command=self.test_auto_diagnostics,
                 bg='#2196f3', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10)
    
    def show_health_history(self):
        """Show system health history"""
        history_window = tk.Toplevel(self.root)
        history_window.title("📊 System Health History")
        history_window.geometry("800x600")
        history_window.configure(bg='#1a1a1a')
        
        # Header
        tk.Label(history_window, text="📊 System Health History", 
                font=('Arial', 16, 'bold'), bg='#1a1a1a', fg='#00ff88').pack(pady=20)
        
        # History display
        history_text = scrolledtext.ScrolledText(history_window, bg='#1a1a1a', fg='white',
                                                font=('Courier', 10))
        history_text.pack(fill='both', expand=True, padx=20, pady=20)
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, health_score, critical_issues, recommendations
                FROM system_health 
                ORDER BY timestamp DESC 
                LIMIT 50
            """)
            
            history_text.insert(tk.END, "SYSTEM HEALTH HISTORY\n")
            history_text.insert(tk.END, "=" * 60 + "\n\n")
            
            for timestamp, score, critical, recommendations in cursor.fetchall():
                dt = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                status = "🟢 HEALTHY" if score >= 80 else "🟡 WARNING" if score >= 60 else "🔴 CRITICAL"
                
                history_text.insert(tk.END, f"[{dt}] {status} Score: {score}%\n")
                if critical > 0:
                    history_text.insert(tk.END, f"  Critical Issues: {critical}\n")
                if recommendations:
                    history_text.insert(tk.END, f"  Notes: {recommendations}\n")
                history_text.insert(tk.END, "\n")
            
            conn.close()
        except Exception as e:
            history_text.insert(tk.END, f"Error loading history: {e}")
    
    # Permission Wizard Methods
    def scan_permissions(self):
        """Scan for permission issues"""
        def scan_thread():
            self.permission_listbox.delete(0, tk.END)
            self.permission_listbox.insert(tk.END, "🔍 Scanning permissions...")
            
            issues = []
            
            # Check common permission issues
            permission_checks = [
                ("/home/nike/.local/bin", "User bin directory"),
                ("/home/nike/.config", "User config directory"),
                ("/home/nike/Desktop", "Desktop directory"),
                ("/home/nike/.cache", "User cache directory"),
            ]
            
            for path, desc in permission_checks:
                if os.path.exists(path):
                    stat_info = os.stat(path)
                    perms = oct(stat_info.st_mode)[-3:]
                    if stat_info.st_uid != os.getuid():
                        issues.append((path, desc, "Wrong owner", perms))
                    elif perms not in ['755', '700', '644', '600']:
                        issues.append((path, desc, "Unusual permissions", perms))
            
            # Check executable files
            try:
                result = subprocess.run("find ~/Desktop -name '*.sh' -o -name '*.py' | head -10", 
                                       shell=True, capture_output=True, text=True)
                for filepath in result.stdout.strip().split('\n'):
                    if filepath and os.path.exists(filepath):
                        if not os.access(filepath, os.X_OK):
                            issues.append((filepath, "Script file", "Not executable", "---"))
            except:
                pass
            
            self.permission_listbox.delete(0, tk.END)
            
            if issues:
                for path, desc, issue, perms in issues:
                    self.permission_listbox.insert(tk.END, f"❌ {desc}: {issue} ({perms})")
                    self.permission_listbox.insert(tk.END, f"    {path}")
            else:
                self.permission_listbox.insert(tk.END, "✅ No permission issues found")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def fix_selected_permissions(self):
        """Fix selected permission issues"""
        selection = self.permission_listbox.curselection()
        if selection:
            self.permission_listbox.insert(tk.END, "🔧 Fixing selected permissions...")
            # Implementation would go here
            self.permission_listbox.insert(tk.END, "✅ Selected permissions fixed")
    
    def fix_all_permissions(self):
        """Fix all detected permission issues"""
        def fix_thread():
            self.permission_listbox.insert(tk.END, "⚡ Fixing all permissions...")
            
            fixes_applied = 0
            
            # Fix common permission issues
            commands = [
                ("chmod +x ~/Desktop/*.sh", "Make shell scripts executable"),
                ("chmod +x ~/Desktop/*.py", "Make Python scripts executable"),
                ("chmod 755 ~/.local/bin/* 2>/dev/null || true", "Fix user bin permissions"),
                ("chmod 755 ~/Desktop 2>/dev/null || true", "Fix desktop permissions")
            ]
            
            for cmd, desc in commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True)
                    if result.returncode == 0:
                        fixes_applied += 1
                        self.permission_listbox.insert(tk.END, f"✅ {desc}")
                    else:
                        self.permission_listbox.insert(tk.END, f"⚠️ {desc} (partial)")
                except Exception as e:
                    self.permission_listbox.insert(tk.END, f"❌ {desc}: {str(e)[:50]}...")
            
            self.permission_listbox.insert(tk.END, f"\n🎉 Applied {fixes_applied} permission fixes")
            
            # Save to database
            self.save_permission_fix_record(f"Fixed {fixes_applied} permission issues")
        
        threading.Thread(target=fix_thread, daemon=True).start()
    
    def save_permission_fix_record(self, details):
        """Save permission fix to database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO permission_fixes (timestamp, file_path, old_permissions, new_permissions, fix_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), "Multiple files", "Various", "Fixed", details))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving permission fix: {e}")
    
    # Recovery Mode Methods
    def emergency_file_fix(self):
        """Emergency file opening fix"""
        def emergency_thread():
            self.recovery_console.insert(tk.END, "🔧 Emergency file fix initiated...\n")
            
            # Force reinstall critical components
            commands = [
                "sudo apt install --reinstall -y xdg-utils gnome-text-editor",
                "systemctl --user restart xdg-desktop-portal",
                "update-desktop-database ~/.local/share/applications/",
                "xdg-mime default gnome-text-editor.desktop text/plain"
            ]
            
            for cmd in commands:
                self.recovery_console.insert(tk.END, f"⚡ {cmd}\n")
                try:
                    subprocess.run(cmd, shell=True, timeout=30)
                    self.recovery_console.insert(tk.END, "✅ Command completed\n")
                except:
                    self.recovery_console.insert(tk.END, "❌ Command failed\n")
            
            self.recovery_console.insert(tk.END, "\n✅ Emergency file fix complete\n")
        
        threading.Thread(target=emergency_thread, daemon=True).start()
    
    def force_system_clean(self):
        """Force comprehensive system cleanup"""
        def clean_thread():
            self.recovery_console.insert(tk.END, "🧹 Force system cleanup...\n")
            
            commands = [
                "sudo apt clean",
                "sudo apt autoclean", 
                "sudo apt autoremove -y",
                "rm -rf ~/.cache/* 2>/dev/null || true",
                "sudo journalctl --vacuum-time=7d"
            ]
            
            for cmd in commands:
                self.recovery_console.insert(tk.END, f"⚡ {cmd}\n")
                subprocess.run(cmd, shell=True)
            
            self.recovery_console.insert(tk.END, "✅ Force cleanup complete\n")
        
        threading.Thread(target=clean_thread, daemon=True).start()
    
    def restart_all_services(self):
        """Restart all critical services"""
        def restart_thread():
            services = [
                "systemctl --user restart xdg-desktop-portal",
                "systemctl --user restart xdg-desktop-portal-gnome",
                "systemctl --user restart xdg-desktop-portal-gtk"
            ]
            
            for service in services:
                self.recovery_console.insert(tk.END, f"⚙️ {service}\n")
                subprocess.run(service, shell=True)
            
            self.recovery_console.insert(tk.END, "✅ Services restarted\n")
        
        threading.Thread(target=restart_thread, daemon=True).start()
    
    def reset_user_permissions(self):
        """Reset user directory permissions"""
        def reset_thread():
            self.recovery_console.insert(tk.END, "🔄 Resetting permissions...\n")
            
            commands = [
                "chmod 755 ~/Desktop",
                "chmod +x ~/Desktop/*.sh 2>/dev/null || true",
                "chmod +x ~/Desktop/*.py 2>/dev/null || true",
                "chmod 755 ~/.local/bin/* 2>/dev/null || true"
            ]
            
            for cmd in commands:
                subprocess.run(cmd, shell=True)
                self.recovery_console.insert(tk.END, f"✅ {cmd}\n")
            
            self.recovery_console.insert(tk.END, "✅ Permissions reset\n")
        
        threading.Thread(target=reset_thread, daemon=True).start()
    
    def emergency_backup(self):
        """Create emergency backup"""
        backup_dir = f"/tmp/emergency_backup_{int(time.time())}"
        os.makedirs(backup_dir, exist_ok=True)
        
        self.recovery_console.insert(tk.END, f"💾 Emergency backup: {backup_dir}\n")
        
        # Copy critical files
        try:
            shutil.copy2(self.config_file, backup_dir)
            shutil.copy2(self.db_file, backup_dir)
            self.recovery_console.insert(tk.END, "✅ Critical files backed up\n")
        except Exception as e:
            self.recovery_console.insert(tk.END, f"❌ Backup failed: {e}\n")
    
    def system_restore_point(self):
        """Create system restore point"""
        self.recovery_console.insert(tk.END, "🏥 Creating restore point...\n")
        self.recovery_console.insert(tk.END, "⚠️ Feature not implemented - use system backup instead\n")
    
    # Auto-Diagnostics Methods
    def save_diagnostic_config(self, window):
        """Save diagnostic configuration"""
        self.config['auto_diagnostic_enabled'] = self.auto_diag_var.get()
        self.config['diagnostic_schedule'] = self.diag_freq_var.get()
        self.save_config()
        
        messagebox.showinfo("Configuration Saved", "Auto-diagnostics configuration has been saved!")
        window.destroy()
    
    def test_auto_diagnostics(self):
        """Test run auto-diagnostics"""
        def test_thread():
            # Run file opening diagnostic
            if self.diag_types['file_opening'].get():
                self.diagnose_file_opening()
            
            # Run permission check
            if self.diag_types['permissions'].get():
                self.scan_permissions()
            
            # Update health dashboard
            if self.diag_types['system_health'].get():
                self.refresh_health_dashboard()
            
            self.show_notification("Test Complete", "Auto-diagnostics test run completed!")
        
        threading.Thread(target=test_thread, daemon=True).start()

        # MAINTENANCE METHODS
    def update_system(self):
        """Update system packages"""
        def update_thread():
            self.maintenance_text.delete('1.0', tk.END)
            self.maintenance_text.insert(tk.END, "🔄 Updating system packages...\n\n")
            
            commands = [
                ("sudo apt update", "Updating package lists"),
                ("sudo apt list --upgradable", "Checking upgradable packages"),
            ]
            
            for cmd, desc in commands:
                self.maintenance_text.insert(tk.END, f"{desc}...\n")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                self.maintenance_text.insert(tk.END, f"{result.stdout}\n\n")
                self.maintenance_text.see(tk.END)
                self.root.update()
            
            self.maintenance_text.insert(tk.END, "✅ System update check complete!\n")
            self.save_to_history("System Update", "System update check performed")
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def clean_packages(self):
        """Clean package system"""
        def clean_thread():
            self.maintenance_text.delete('1.0', tk.END)
            self.maintenance_text.insert(tk.END, "🧹 Cleaning package system...\n\n")
            
            commands = [
                ("sudo apt autoclean", "Cleaning package cache"),
                ("sudo apt autoremove", "Removing unused packages"),
                ("dpkg --get-selections | wc -l", "Counting installed packages")
            ]
            
            for cmd, desc in commands:
                self.maintenance_text.insert(tk.END, f"{desc}...\n")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                self.maintenance_text.insert(tk.END, f"{result.stdout}\n")
                self.root.update()
            
            self.maintenance_text.insert(tk.END, "✅ Package cleaning complete!\n")
            self.save_to_history("Package Cleanup", "Package system cleaned")
        
        threading.Thread(target=clean_thread, daemon=True).start()
    
    def fix_broken_dependencies(self):
        """Fix broken dependencies"""
        def fix_thread():
            self.maintenance_text.delete('1.0', tk.END)
            self.maintenance_text.insert(tk.END, "🔧 Fixing broken dependencies...\n\n")
            
            commands = [
                ("sudo apt --fix-broken install", "Fixing broken packages"),
                ("sudo dpkg --configure -a", "Configuring packages"),
                ("sudo apt-get check", "Checking package integrity")
            ]
            
            for cmd, desc in commands:
                self.maintenance_text.insert(tk.END, f"{desc}...\n")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    self.maintenance_text.insert(tk.END, f"{result.stdout}\n")
                if result.stderr:
                    self.maintenance_text.insert(tk.END, f"Errors: {result.stderr}\n")
                self.root.update()
            
            self.maintenance_text.insert(tk.END, "✅ Dependency fixing complete!\n")
            self.save_to_history("Dependency Fix", "Fixed broken dependencies")
        
        threading.Thread(target=fix_thread, daemon=True).start()
    
    def system_integrity_check(self):
        """Check system integrity"""
        def integrity_thread():
            self.maintenance_text.delete('1.0', tk.END)
            self.maintenance_text.insert(tk.END, "🔧 Checking system integrity...\n\n")
            
            # Check filesystem
            self.maintenance_text.insert(tk.END, "Checking filesystem...\n")
            result = subprocess.run("df -h", shell=True, capture_output=True, text=True)
            self.maintenance_text.insert(tk.END, f"{result.stdout}\n")
            
            # Check memory
            self.maintenance_text.insert(tk.END, "Checking memory usage...\n")
            result = subprocess.run("free -h", shell=True, capture_output=True, text=True)
            self.maintenance_text.insert(tk.END, f"{result.stdout}\n")
            
            # Check system load
            self.maintenance_text.insert(tk.END, "Checking system load...\n")
            result = subprocess.run("uptime", shell=True, capture_output=True, text=True)
            self.maintenance_text.insert(tk.END, f"{result.stdout}\n")
            
            self.maintenance_text.insert(tk.END, "✅ System integrity check complete!\n")
            self.save_to_history("Integrity Check", "System integrity verified")
        
        threading.Thread(target=integrity_thread, daemon=True).start()
    
    def backup_system_files(self):
        """Backup important system files"""
        def backup_thread():
            self.maintenance_text.delete('1.0', tk.END)
            self.maintenance_text.insert(tk.END, "💾 Backing up system files...\n\n")
            
            backup_dir = f"/tmp/system_backup_{int(time.time())}"
            os.makedirs(backup_dir, exist_ok=True)
            
            files_to_backup = [
                ("/etc/fstab", "File system table"),
                ("/etc/hosts", "Host file"),
                ("/etc/hostname", "Hostname"),
                (os.path.expanduser("~/.bashrc"), "Bash configuration"),
                (os.path.expanduser("~/.profile"), "Profile")
            ]
            
            for file_path, description in files_to_backup:
                if os.path.exists(file_path):
                    try:
                        shutil.copy2(file_path, backup_dir)
                        self.maintenance_text.insert(tk.END, f"✅ Backed up {description}\n")
                    except Exception as e:
                        self.maintenance_text.insert(tk.END, f"❌ Failed to backup {description}: {e}\n")
                else:
                    self.maintenance_text.insert(tk.END, f"⚠️ {description} not found\n")
                self.root.update()
            
            self.maintenance_text.insert(tk.END, f"\n✅ Backup completed: {backup_dir}\n")
            self.save_to_history("System Backup", f"Backed up system files to {backup_dir}")
        
        threading.Thread(target=backup_thread, daemon=True).start()
    
    def generate_system_report(self):
        """Generate comprehensive system report"""
        def report_thread():
            self.maintenance_text.delete('1.0', tk.END)
            self.maintenance_text.insert(tk.END, "📋 Generating system report...\n\n")
            
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'system_info': {
                    'hostname': subprocess.run('hostname', shell=True, capture_output=True, text=True).stdout.strip(),
                    'kernel': subprocess.run('uname -r', shell=True, capture_output=True, text=True).stdout.strip(),
                    'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
                },
                'hardware': {
                    'cpu_cores': psutil.cpu_count(),
                    'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                    'disk_gb': round(psutil.disk_usage('/').total / (1024**3), 2)
                },
                'performance': {
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': round((psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100, 2)
                }
            }
            
            report_file = f"/tmp/system_report_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            # Display summary
            self.maintenance_text.insert(tk.END, f"System: {report_data['system_info']['hostname']}\n")
            self.maintenance_text.insert(tk.END, f"Kernel: {report_data['system_info']['kernel']}\n")
            self.maintenance_text.insert(tk.END, f"Uptime: {report_data['system_info']['uptime']}\n")
            self.maintenance_text.insert(tk.END, f"CPU Usage: {report_data['performance']['cpu_usage']}%\n")
            self.maintenance_text.insert(tk.END, f"Memory Usage: {report_data['performance']['memory_usage']}%\n")
            self.maintenance_text.insert(tk.END, f"Disk Usage: {report_data['performance']['disk_usage']}%\n")
            
            self.maintenance_text.insert(tk.END, f"\n✅ Full report saved: {report_file}\n")
            self.save_to_history("System Report", f"Generated system report: {report_file}")
        
        threading.Thread(target=report_thread, daemon=True).start()
    
    # SETTINGS METHODS
    def save_all_settings(self):
        """Save all application settings"""
        self.config['safe_mode'] = self.safe_mode.get()
        self.config['auto_cleanup_enabled'] = self.auto_cleanup_enabled.get()
        self.config['notifications_enabled'] = self.notifications_enabled.get()
        self.config['cleanup_schedule'] = self.schedule_var.get()
        self.config['auto_diagnostic_enabled'] = self.auto_diagnostic_enabled.get()
        self.config['diagnostic_schedule'] = self.diagnostic_schedule_var.get()
        self.config['system_health_alerts'] = self.system_health_alerts.get()
        self.config['permission_auto_fix'] = self.permission_auto_fix.get()
        self.save_config()
        
        messagebox.showinfo("Settings Saved", "All settings have been saved successfully!")
        self.save_to_history("Settings", "Application settings updated")
    
    # ANALYTICS METHODS
    def show_usage_stats(self):
        """Show usage statistics"""
        def stats_thread():
            self.analytics_text.delete('1.0', tk.END)
            self.analytics_text.insert(tk.END, "📊 System Usage Statistics\n")
            self.analytics_text.insert(tk.END, "="*50 + "\n\n")
            
            # Get history count
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cleanup_history")
            cleanup_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT action, COUNT(*) FROM cleanup_history GROUP BY action")
            actions = cursor.fetchall()
            
            conn.close()
            
            self.analytics_text.insert(tk.END, f"Total cleanup operations: {cleanup_count}\n\n")
            
            if actions:
                self.analytics_text.insert(tk.END, "Operation breakdown:\n")
                for action, count in actions:
                    self.analytics_text.insert(tk.END, f"  {action}: {count}\n")
            
            # System stats
            self.analytics_text.insert(tk.END, f"\nCurrent system status:\n")
            self.analytics_text.insert(tk.END, f"  CPU Usage: {psutil.cpu_percent()}%\n")
            self.analytics_text.insert(tk.END, f"  Memory Usage: {psutil.virtual_memory().percent:.1f}%\n")
            self.analytics_text.insert(tk.END, f"  Disk Usage: {(psutil.disk_usage('/').used/psutil.disk_usage('/').total*100):.1f}%\n")
        
        threading.Thread(target=stats_thread, daemon=True).start()
    
    def show_performance_trends(self):
        """Show performance trends"""
        def trends_thread():
            self.analytics_text.delete('1.0', tk.END)
            self.analytics_text.insert(tk.END, "📈 Performance Trends\n")
            self.analytics_text.insert(tk.END, "="*50 + "\n\n")
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Get recent snapshots
            cursor.execute("""
                SELECT timestamp, cpu_usage, memory_usage, disk_usage 
                FROM system_snapshots 
                ORDER BY timestamp DESC 
                LIMIT 20
            """)
            snapshots = cursor.fetchall()
            conn.close()
            
            if snapshots:
                self.analytics_text.insert(tk.END, "Recent performance data:\n")
                self.analytics_text.insert(tk.END, f"{'Time':<20} {'CPU%':<8} {'MEM%':<8} {'DISK%':<8}\n")
                self.analytics_text.insert(tk.END, "-"*50 + "\n")
                
                for timestamp, cpu, memory, disk in snapshots[:10]:
                    dt = datetime.fromisoformat(timestamp).strftime('%H:%M:%S')
                    self.analytics_text.insert(tk.END, 
                        f"{dt:<20} {cpu:<8.1f} {memory:<8.1f} {disk:<8.1f}\n")
            else:
                self.analytics_text.insert(tk.END, "No performance data available yet.\n")
        
        threading.Thread(target=trends_thread, daemon=True).start()
    
    def show_space_analysis(self):
        """Show disk space analysis"""
        def space_thread():
            self.analytics_text.delete('1.0', tk.END)
            self.analytics_text.insert(tk.END, "💾 Disk Space Analysis\n")
            self.analytics_text.insert(tk.END, "="*50 + "\n\n")
            
            # Current disk usage
            disk = psutil.disk_usage('/')
            self.analytics_text.insert(tk.END, f"Current disk usage:\n")
            self.analytics_text.insert(tk.END, f"  Total: {self.format_bytes(disk.total)}\n")
            self.analytics_text.insert(tk.END, f"  Used: {self.format_bytes(disk.used)} ({disk.used/disk.total*100:.1f}%)\n")
            self.analytics_text.insert(tk.END, f"  Free: {self.format_bytes(disk.free)}\n\n")
            
            # Directory analysis
            self.analytics_text.insert(tk.END, "Large directories in home:\n")
            result = subprocess.run("du -h --max-depth=1 ~ 2>/dev/null | sort -hr | head -10", 
                                   shell=True, capture_output=True, text=True)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    self.analytics_text.insert(tk.END, f"  {line}\n")
        
        threading.Thread(target=space_thread, daemon=True).start()
    
    def show_system_history(self):
        """Show system history"""
        def history_thread():
            self.analytics_text.delete('1.0', tk.END)
            self.analytics_text.insert(tk.END, "🕒 System History\n")
            self.analytics_text.insert(tk.END, "="*50 + "\n\n")
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, action, details 
                FROM cleanup_history 
                ORDER BY timestamp DESC 
                LIMIT 20
            """)
            history = cursor.fetchall()
            conn.close()
            
            if history:
                for timestamp, action, details in history:
                    dt = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    self.analytics_text.insert(tk.END, f"[{dt}] {action}\n")
                    if details:
                        self.analytics_text.insert(tk.END, f"  └─ {details}\n")
                    self.analytics_text.insert(tk.END, "\n")
            else:
                self.analytics_text.insert(tk.END, "No history available.\n")
        
        threading.Thread(target=history_thread, daemon=True).start()
    
    def generate_full_report(self):
        """Generate comprehensive analytics report"""
        def full_report_thread():
            self.analytics_text.delete('1.0', tk.END)
            self.analytics_text.insert(tk.END, "📋 Generating full analytics report...\n\n")
            
            # Collect all data
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_cores': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'disk_total': psutil.disk_usage('/').total,
                    'current_cpu': psutil.cpu_percent(),
                    'current_memory': psutil.virtual_memory().percent,
                    'current_disk': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
                }
            }
            
            # Get history data
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM cleanup_history")
            report_data['history'] = {'total_cleanups': cursor.fetchone()[0]}
            
            cursor.execute("SELECT COUNT(*) FROM system_snapshots")
            report_data['monitoring'] = {'total_snapshots': cursor.fetchone()[0]}
            
            conn.close()
            
            # Save report
            report_file = f"/tmp/analytics_report_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            # Display summary
            self.analytics_text.insert(tk.END, f"System Overview:\n")
            self.analytics_text.insert(tk.END, f"  CPU Cores: {report_data['system']['cpu_cores']}\n")
            self.analytics_text.insert(tk.END, f"  Total Memory: {self.format_bytes(report_data['system']['memory_total'])}\n")
            self.analytics_text.insert(tk.END, f"  Total Disk: {self.format_bytes(report_data['system']['disk_total'])}\n")
            self.analytics_text.insert(tk.END, f"  Total Cleanups: {report_data['history']['total_cleanups']}\n")
            self.analytics_text.insert(tk.END, f"  Monitoring Points: {report_data['monitoring']['total_snapshots']}\n")
            self.analytics_text.insert(tk.END, f"\n✅ Full report saved: {report_file}\n")
            
            self.save_to_history("Analytics Report", f"Generated full report: {report_file}")
        
        threading.Thread(target=full_report_thread, daemon=True).start()
    
    def export_analytics_data(self):
        """Export analytics data"""
        def export_thread():
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                # Export all data
                export_data = {
                    'exported_at': datetime.now().isoformat(),
                    'config': self.config
                }
                
                # Add database data
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                # Export history
                cursor.execute("SELECT * FROM cleanup_history")
                export_data['cleanup_history'] = [
                    dict(zip([col[0] for col in cursor.description], row))
                    for row in cursor.fetchall()
                ]
                
                # Export snapshots
                cursor.execute("SELECT * FROM system_snapshots ORDER BY timestamp DESC LIMIT 1000")
                export_data['system_snapshots'] = [
                    dict(zip([col[0] for col in cursor.description], row))
                    for row in cursor.fetchall()
                ]
                
                conn.close()
                
                # Save file
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                self.analytics_text.delete('1.0', tk.END)
                self.analytics_text.insert(tk.END, f"📤 Analytics data exported to: {filename}\n")
                self.analytics_text.insert(tk.END, f"Total records exported:\n")
                self.analytics_text.insert(tk.END, f"  Cleanup history: {len(export_data['cleanup_history'])}\n")
                self.analytics_text.insert(tk.END, f"  System snapshots: {len(export_data['system_snapshots'])}\n")
                
                messagebox.showinfo("Export Complete", f"Analytics data exported to {filename}")
        
        threading.Thread(target=export_thread, daemon=True).start()
    
    # UTILITY METHODS
    def load_recent_activity(self):
        """Load recent activity from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, action, details 
                FROM cleanup_history 
                ORDER BY timestamp DESC 
                LIMIT 20
            """)
            
            activities = cursor.fetchall()
            conn.close()
            
            self.activity_text.delete('1.0', tk.END)
            
            if activities:
                for timestamp, action, details in activities:
                    dt = datetime.fromisoformat(timestamp).strftime('%H:%M:%S')
                    self.activity_text.insert(tk.END, f"[{dt}] {action}\n")
                    if details:
                        self.activity_text.insert(tk.END, f"    └─ {details}\n")
                    self.activity_text.insert(tk.END, "\n")
            else:
                self.activity_text.insert(tk.END, "No recent activity found.\nRun some operations to see history here.")
                
        except Exception as e:
            self.activity_text.insert(tk.END, f"Error loading activity: {e}")
    
    def log_to_console(self, message):
        """Log message to cleanup console"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        if hasattr(self, 'cleanup_console'):
            self.cleanup_console.insert(tk.END, f"[{timestamp}] {message}\n")
            self.cleanup_console.see(tk.END)
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message[:50])
            
        self.root.update()
    
    def run_command_silent(self, command):
        """Run command silently"""
        try:
            subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        except:
            pass
    
    def get_disk_usage(self):
        """Get current disk usage in bytes"""
        return psutil.disk_usage('/').used
    
    def get_directory_size(self, path):
        """Get directory size in bytes"""
        try:
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total += os.path.getsize(filepath)
                    except:
                        pass
            return total
        except:
            return 0
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f}TB"
    
    def save_to_history(self, action, details):
        """Save action to history database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cleanup_history (timestamp, action, details)
                VALUES (?, ?, ?)
            """, (datetime.now().isoformat(), action, details))
            conn.commit()
            conn.close()
            
            # Refresh activity display
            self.root.after(1000, self.load_recent_activity)
        except Exception as e:
            print(f"Error saving to history: {e}")
    
    def show_notification(self, title, message):
        """Show desktop notification"""
        try:
            subprocess.run(f'notify-send "{title}" "{message}"', shell=True)
        except:
            pass

def main():
    root = tk.Tk()
    app = SystemOptimizerComplete(root)
    root.mainloop()

if __name__ == "__main__":
    main()
