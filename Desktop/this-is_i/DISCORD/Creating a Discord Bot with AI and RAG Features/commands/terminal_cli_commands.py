#!/usr/bin/env python3
"""
Terminal and CLI Integration Commands
Advanced terminal access and Discord CLI integration
"""

import discord
from discord.ext import commands
from command_manager import command
import asyncio
import os
import sys
import subprocess
import tempfile
import json
import shlex
from pathlib import Path
from datetime import datetime

# Security configuration
ALLOWED_COMMANDS = {
    # System info
    'ls', 'pwd', 'whoami', 'date', 'uptime', 'df', 'free', 'ps',
    # File operations (safe)
    'cat', 'head', 'tail', 'wc', 'grep', 'find', 'file',
    # Network tools
    'ping', 'nslookup', 'dig', 'curl', 'wget',
    # Security tools (authorized use only)
    'nmap', 'nikto', 'dirb', 'gobuster', 'sqlmap',
    # Development tools
    'git', 'python3', 'node', 'npm', 'pip3',
    # Discord CLI
    'discord-cli', 'dcli'
}

DANGEROUS_COMMANDS = {
    'rm', 'rmdir', 'mv', 'cp', 'chmod', 'chown', 'sudo', 'su',
    'dd', 'fdisk', 'mkfs', 'mount', 'umount', 'kill', 'killall',
    'systemctl', 'service', 'reboot', 'shutdown', 'halt'
}

# Command timeout in seconds
COMMAND_TIMEOUT = 30

@command("terminal", "Execute terminal commands (authorized users only)")
async def terminal_command(ctx, *, command: str):
    """
    Execute terminal commands with security restrictions
    Usage: /terminal <command>
    """
    # Security check
    if not is_authorized_user(ctx.author.id):
        await ctx.send("❌ **Access Denied** - You are not authorized to use terminal commands.")
        return
    
    # Parse command
    try:
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            await ctx.send("❌ No command provided!")
            return
        
        base_command = cmd_parts[0]
        
        # Security validation
        if base_command in DANGEROUS_COMMANDS:
            await ctx.send(f"❌ **DANGEROUS COMMAND BLOCKED**: `{base_command}`\n"
                          f"This command is not allowed for security reasons.")
            return
        
        if base_command not in ALLOWED_COMMANDS:
            await ctx.send(f"❌ **COMMAND NOT ALLOWED**: `{base_command}`\n"
                          f"Only whitelisted commands are permitted.\n"
                          f"Use `/terminalhelp` to see allowed commands.")
            return
        
        await ctx.send(f"💻 Executing: `{command}`")
        
        # Execute command with timeout
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT,
                cwd=os.path.expanduser("~")
            )
            
            # Format output
            output = result.stdout
            error = result.stderr
            
            if len(output) > 1900:
                output = output[:1900] + "\n... (output truncated)"
            
            if len(error) > 500:
                error = error[:500] + "\n... (error truncated)"
            
            embed = discord.Embed(
                title=f"💻 Terminal Output",
                color=0x00ff00 if result.returncode == 0 else 0xff0000,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Command", value=f"`{command}`", inline=False)
            embed.add_field(name="Return Code", value=str(result.returncode), inline=True)
            embed.add_field(name="User", value=ctx.author.mention, inline=True)
            
            if output:
                embed.add_field(name="Output", value=f"```\n{output}\n```", inline=False)
            
            if error:
                embed.add_field(name="Error", value=f"```\n{error}\n```", inline=False)
            
            embed.set_footer(text="⚠️ Terminal access is logged and monitored")
            
            await ctx.send(embed=embed)
            
            # Log command execution
            log_terminal_command(ctx.author.id, ctx.author.name, command, result.returncode)
            
        except subprocess.TimeoutExpired:
            await ctx.send(f"⏰ **Command Timeout** - Command exceeded {COMMAND_TIMEOUT} seconds")
        except FileNotFoundError:
            await ctx.send(f"❌ **Command Not Found**: `{base_command}`")
        except Exception as e:
            await ctx.send(f"❌ **Execution Error**: {e}")
    
    except Exception as e:
        await ctx.send(f"❌ **Command Parse Error**: {e}")

@command("terminalhelp", "Show allowed terminal commands")
async def terminal_help(ctx):
    """
    Show list of allowed terminal commands
    Usage: /terminalhelp
    """
    embed = discord.Embed(
        title="💻 Terminal Commands Help",
        description="List of allowed terminal commands",
        color=0x3498db,
        timestamp=datetime.now()
    )
    
    # Group commands by category
    categories = {
        "📁 File Operations": ['ls', 'pwd', 'cat', 'head', 'tail', 'wc', 'grep', 'find', 'file'],
        "🖥️ System Info": ['whoami', 'date', 'uptime', 'df', 'free', 'ps'],
        "🌐 Network Tools": ['ping', 'nslookup', 'dig', 'curl', 'wget'],
        "🔒 Security Tools": ['nmap', 'nikto', 'dirb', 'gobuster', 'sqlmap'],
        "⚙️ Development": ['git', 'python3', 'node', 'npm', 'pip3'],
        "💬 Discord CLI": ['discord-cli', 'dcli']
    }
    
    for category, commands in categories.items():
        command_list = ", ".join([f"`{cmd}`" for cmd in commands])
        embed.add_field(name=category, value=command_list, inline=False)
    
    embed.add_field(
        name="⚠️ Security Notice",
        value="• Only authorized users can execute commands\n"
              "• All commands are logged and monitored\n"
              "• Dangerous commands are blocked\n"
              "• Commands have a 30-second timeout",
        inline=False
    )
    
    embed.set_footer(text="Use /terminal <command> to execute")
    
    await ctx.send(embed=embed)

@command("nmap", "Network scanning with Nmap (authorized only)")
async def nmap_scan(ctx, target: str, *, options: str = "-sV -sC"):
    """
    Perform authorized Nmap scan
    Usage: /nmap <target> [options]
    """
    if not is_authorized_user(ctx.author.id):
        await ctx.send("❌ **Access Denied** - Nmap requires authorization.")
        return
    
    # Authorization warning
    auth_embed = discord.Embed(
        title="🔍 NMAP SCAN AUTHORIZATION",
        description="**⚠️ LEGAL WARNING ⚠️**\n\n"
                   "Network scanning must only be performed on:\n"
                   "• Your own systems\n"
                   "• Systems you have written permission to test\n"
                   "• Authorized penetration testing targets\n\n"
                   "**Unauthorized scanning is illegal!**",
        color=0xff9900,
        timestamp=datetime.now()
    )
    
    await ctx.send(embed=auth_embed)
    
    # Confirmation required
    await ctx.send("**Type 'AUTHORIZED' to confirm you have permission to scan this target:**")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content == 'AUTHORIZED'
    
    try:
        await ctx.bot.wait_for('message', check=check, timeout=30.0)
        
        await ctx.send(f"🔍 **AUTHORIZED NMAP SCAN STARTED**\nTarget: `{target}`\nOptions: `{options}`")
        
        # Execute nmap
        nmap_command = f"nmap {options} {target}"
        
        try:
            result = subprocess.run(
                shlex.split(nmap_command),
                capture_output=True,
                text=True,
                timeout=120  # Longer timeout for nmap
            )
            
            output = result.stdout
            if len(output) > 1900:
                output = output[:1900] + "\n... (output truncated)"
            
            embed = discord.Embed(
                title="🔍 Nmap Scan Results (AUTHORIZED)",
                color=0x00ff7f,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Target", value=target, inline=True)
            embed.add_field(name="Options", value=options, inline=True)
            embed.add_field(name="Return Code", value=str(result.returncode), inline=True)
            
            if output:
                embed.add_field(name="Scan Results", value=f"```\n{output}\n```", inline=False)
            
            if result.stderr:
                embed.add_field(name="Errors", value=f"```\n{result.stderr[:500]}\n```", inline=False)
            
            embed.set_footer(text="🔒 Authorized scan - All activity logged")
            
            await ctx.send(embed=embed)
            
            # Log scan
            log_security_activity(ctx.author.id, "nmap_scan", f"Target: {target}, Options: {options}")
            
        except subprocess.TimeoutExpired:
            await ctx.send("⏰ **Nmap Timeout** - Scan exceeded 2 minutes")
        except Exception as e:
            await ctx.send(f"❌ **Nmap Error**: {e}")
    
    except asyncio.TimeoutError:
        await ctx.send("⏰ **Authorization Timeout** - Scan cancelled")

@command("dcli", "Discord CLI integration")
async def discord_cli(ctx, *, command: str):
    """
    Execute Discord CLI commands
    Usage: /dcli <command>
    """
    if not is_authorized_user(ctx.author.id):
        await ctx.send("❌ **Access Denied** - Discord CLI requires authorization.")
        return
    
    await ctx.send(f"💬 Executing Discord CLI: `{command}`")
    
    try:
        # Check if discord-cli is installed
        dcli_path = subprocess.run(['which', 'discord-cli'], capture_output=True, text=True)
        if dcli_path.returncode != 0:
            await ctx.send("❌ **Discord CLI not found** - Please install discord-cli first.")
            return
        
        # Execute discord-cli command
        full_command = f"discord-cli {command}"
        
        result = subprocess.run(
            shlex.split(full_command),
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT
        )
        
        output = result.stdout
        error = result.stderr
        
        if len(output) > 1900:
            output = output[:1900] + "\n... (output truncated)"
        
        embed = discord.Embed(
            title="💬 Discord CLI Output",
            color=0x7289da,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Command", value=f"`{command}`", inline=False)
        embed.add_field(name="Return Code", value=str(result.returncode), inline=True)
        
        if output:
            embed.add_field(name="Output", value=f"```\n{output}\n```", inline=False)
        
        if error:
            embed.add_field(name="Error", value=f"```\n{error[:500]}\n```", inline=False)
        
        embed.set_footer(text="💬 Discord CLI Integration")
        
        await ctx.send(embed=embed)
        
    except subprocess.TimeoutExpired:
        await ctx.send(f"⏰ **Discord CLI Timeout** - Command exceeded {COMMAND_TIMEOUT} seconds")
    except Exception as e:
        await ctx.send(f"❌ **Discord CLI Error**: {e}")

@command("channelexportcli", "Export channel using Discord CLI")
async def channel_export_cli(ctx, channel_name: str = None):
    """
    Export channel using Discord CLI
    Usage: /channelexportcli [channel_name]
    """
    if not is_authorized_user(ctx.author.id):
        await ctx.send("❌ **Access Denied** - Channel export requires authorization.")
        return
    
    target_channel = channel_name or ctx.channel.name
    
    await ctx.send(f"📤 Exporting channel `#{target_channel}` using Discord CLI...")
    
    try:
        # Use discord-cli to export channel
        export_command = f'discord-cli channels {ctx.guild.id} --name "{target_channel}" --export'
        
        result = subprocess.run(
            shlex.split(export_command),
            capture_output=True,
            text=True,
            timeout=60  # Longer timeout for export
        )
        
        if result.returncode == 0:
            embed = discord.Embed(
                title="📤 Channel Export Complete",
                description=f"Successfully exported `#{target_channel}`",
                color=0x00ff7f,
                timestamp=datetime.now()
            )
            
            if result.stdout:
                embed.add_field(name="Export Details", value=f"```\n{result.stdout[:1000]}\n```", inline=False)
            
            embed.set_footer(text="💬 Exported via Discord CLI")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ **Export Failed**: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        await ctx.send("⏰ **Export Timeout** - Export exceeded 60 seconds")
    except Exception as e:
        await ctx.send(f"❌ **Export Error**: {e}")

@command("createcommand", "Create custom command interactively")
async def create_custom_command(ctx, command_name: str, *, description: str = ""):
    """
    Create a custom command interactively
    Usage: /createcommand <name> [description]
    """
    if not is_authorized_user(ctx.author.id):
        await ctx.send("❌ **Access Denied** - Command creation requires authorization.")
        return
    
    # Validate command name
    if not command_name.isalnum():
        await ctx.send("❌ Command name must be alphanumeric!")
        return
    
    embed = discord.Embed(
        title="⚙️ Custom Command Creator",
        description=f"Creating command: `/{command_name}`\n"
                   f"Description: {description or 'No description'}",
        color=0x00ff7f,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="Command Types",
        value="1️⃣ Simple text response\n"
              "2️⃣ Embed response\n"
              "3️⃣ AI-powered response\n"
              "4️⃣ Terminal command\n"
              "5️⃣ Custom Python function",
        inline=False
    )
    
    embed.set_footer(text="React with the number of your choice")
    
    msg = await ctx.send(embed=embed)
    
    # Add reactions
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for reaction in reactions:
        await msg.add_reaction(reaction)
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in reactions and reaction.message.id == msg.id
    
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        command_type = reactions.index(str(reaction.emoji)) + 1
        
        # Generate command based on type
        if command_type == 1:
            template = generate_simple_command_template(command_name, description)
        elif command_type == 2:
            template = generate_embed_command_template(command_name, description)
        elif command_type == 3:
            template = generate_ai_command_template(command_name, description)
        elif command_type == 4:
            template = generate_terminal_command_template(command_name, description)
        elif command_type == 5:
            template = generate_custom_command_template(command_name, description)
        
        # Save command file
        commands_dir = Path(__file__).parent
        command_file = commands_dir / f"custom_{command_name}.py"
        
        with open(command_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        embed = discord.Embed(
            title="✅ Custom Command Created!",
            description=f"Command `/{command_name}` has been created successfully!",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="File", value=str(command_file), inline=False)
        embed.add_field(name="Next Steps", value="Restart the bot to load the new command", inline=False)
        
        await ctx.send(embed=embed)
        
    except asyncio.TimeoutError:
        await ctx.send("⏰ **Timeout** - Command creation cancelled")

# Helper functions
def is_authorized_user(user_id: int) -> bool:
    """Check if user is authorized for terminal/CLI access"""
    # Add your authorization logic here
    # For now, return True for demonstration
    return True

def log_terminal_command(user_id: int, username: str, command: str, return_code: int):
    """Log terminal command execution"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "username": username,
        "command": command,
        "return_code": return_code,
        "type": "terminal_command"
    }
    
    log_file = Path(__file__).parent.parent / "terminal_logs.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')

def log_security_activity(user_id: int, activity: str, details: str):
    """Log security-related activities"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "activity": activity,
        "details": details,
        "type": "security_activity"
    }
    
    log_file = Path(__file__).parent.parent / "security_logs.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')

def generate_simple_command_template(name: str, description: str) -> str:
    """Generate simple command template"""
    return f'''#!/usr/bin/env python3
"""
Custom Command: {name}
Description: {description}
"""

import discord
from discord.ext import commands
from command_manager import command

@command("{name}", "{description}")
async def {name}(ctx, *args):
    """
    {name} command
    Usage: /{name} [arguments]
    """
    response = f"🤖 {name} command executed!"
    
    if args:
        response += f"\\nArguments: {{' '.join(args)}}"
    
    await ctx.send(response)
'''

def generate_embed_command_template(name: str, description: str) -> str:
    """Generate embed command template"""
    return f'''#!/usr/bin/env python3
"""
Custom Command: {name}
Description: {description}
"""

import discord
from discord.ext import commands
from command_manager import command
from datetime import datetime

@command("{name}", "{description}")
async def {name}(ctx, *args):
    """
    {name} command
    Usage: /{name} [arguments]
    """
    embed = discord.Embed(
        title="🤖 {name.title()} Command",
        description="{description}",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="User", value=ctx.author.mention, inline=True)
    embed.add_field(name="Channel", value=ctx.channel.name, inline=True)
    
    if args:
        embed.add_field(name="Arguments", value=' '.join(args), inline=False)
    
    embed.set_footer(text=f"Command: /{name}")
    
    await ctx.send(embed=embed)
'''

def generate_ai_command_template(name: str, description: str) -> str:
    """Generate AI command template"""
    return f'''#!/usr/bin/env python3
"""
Custom Command: {name}
Description: {description}
"""

import discord
from discord.ext import commands
from command_manager import command
import sys
from pathlib import Path

# Add ollama integration to path
sys.path.append(str(Path(__file__).parent.parent / "ollama_integration"))
from ollama_integration import OllamaIntegration

ollama = OllamaIntegration()

@command("{name}", "{description}")
async def {name}(ctx, *, query: str = ""):
    """
    {name} command with AI integration
    Usage: /{name} <query>
    """
    if not query:
        await ctx.send("❌ Please provide a query. Usage: `/{name} <query>`")
        return
    
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!** Please start Ollama first.")
        return
    
    await ctx.send("🤔 Processing with AI...")
    
    try:
        prompt = f"You are helping with the {name} command. User query: {{query}}"
        ai_response = ollama.chat(prompt, str(ctx.author.id), "{name}_session")
        
        embed = discord.Embed(
            title="🤖 AI Response - {name.title()}",
            description=ai_response,
            color=0x00ff7f
        )
        embed.add_field(name="Query", value=query[:100], inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {{e}}")
'''

def generate_terminal_command_template(name: str, description: str) -> str:
    """Generate terminal command template"""
    return f'''#!/usr/bin/env python3
"""
Custom Command: {name}
Description: {description}
"""

import discord
from discord.ext import commands
from command_manager import command
import subprocess
import shlex

@command("{name}", "{description}")
async def {name}(ctx, *, command: str = ""):
    """
    {name} command with terminal integration
    Usage: /{name} <terminal_command>
    """
    if not command:
        await ctx.send("❌ Please provide a terminal command. Usage: `/{name} <command>`")
        return
    
    # Add your authorization check here
    # if not is_authorized_user(ctx.author.id):
    #     await ctx.send("❌ Access denied")
    #     return
    
    await ctx.send(f"💻 Executing: `{{command}}`")
    
    try:
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout[:1900] if result.stdout else "No output"
        
        embed = discord.Embed(
            title="💻 Terminal Output - {name.title()}",
            color=0x00ff00 if result.returncode == 0 else 0xff0000
        )
        
        embed.add_field(name="Command", value=f"`{{command}}`", inline=False)
        embed.add_field(name="Output", value=f"```\\n{{output}}\\n```", inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {{e}}")
'''

def generate_custom_command_template(name: str, description: str) -> str:
    """Generate custom Python function template"""
    return f'''#!/usr/bin/env python3
"""
Custom Command: {name}
Description: {description}
"""

import discord
from discord.ext import commands
from command_manager import command
from datetime import datetime

@command("{name}", "{description}")
async def {name}(ctx, *args):
    """
    {name} command - Custom Python function
    Usage: /{name} [arguments]
    """
    # Add your custom logic here
    
    # Example: Process arguments
    if args:
        processed_args = [arg.upper() for arg in args]
        result = f"Processed arguments: {{', '.join(processed_args)}}"
    else:
        result = "No arguments provided"
    
    # Example: Create response
    embed = discord.Embed(
        title="⚙️ {name.title()} - Custom Function",
        description=result,
        color=0x9b59b6,
        timestamp=datetime.now()
    )
    
    # Example: Add fields
    embed.add_field(name="User", value=ctx.author.mention, inline=True)
    embed.add_field(name="Arguments Count", value=str(len(args)), inline=True)
    
    # Example: Custom logic
    if len(args) > 3:
        embed.add_field(name="Status", value="Many arguments!", inline=False)
    elif len(args) > 0:
        embed.add_field(name="Status", value="Some arguments", inline=False)
    else:
        embed.add_field(name="Status", value="No arguments", inline=False)
    
    embed.set_footer(text="Custom Python Function")
    
    await ctx.send(embed=embed)
'''

