#!/usr/bin/env python3
"""
Advanced Commands Module
Advanced features for the Discord bot including file operations, system monitoring, and enhanced AI features
"""

import discord
from discord.ext import commands
from command_manager import command
import os
import sys
import psutil
import asyncio
import json
from pathlib import Path
from datetime import datetime
import requests

# Add ollama integration to path
sys.path.append(str(Path(__file__).parent.parent / "ollama_integration"))
from ollama_integration import OllamaIntegration

@command("system", "Show system information and bot statistics")
async def system_info(ctx):
    """Show detailed system information"""
    try:
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get bot info
        ollama = OllamaIntegration()
        ollama_status = ollama.check_ollama_status()
        
        embed = discord.Embed(
            title="🖥️ System Information",
            description="Current system and bot statistics",
            color=0x00ff00
        )
        
        # System stats
        embed.add_field(
            name="💻 System Resources",
            value=f"CPU: {cpu_percent}%\n"
                  f"RAM: {memory.percent}% ({memory.used // (1024**3)}GB/{memory.total // (1024**3)}GB)\n"
                  f"Disk: {disk.percent}% ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)",
            inline=False
        )
        
        # Bot stats
        embed.add_field(
            name="🤖 Bot Statistics",
            value=f"Guilds: {len(ctx.bot.guilds)}\n"
                  f"Users: {len(ctx.bot.users)}\n"
                  f"Latency: {round(ctx.bot.latency * 1000)}ms\n"
                  f"Ollama: {'🟢 Online' if ollama_status else '🔴 Offline'}",
            inline=False
        )
        
        # Process info
        process = psutil.Process()
        embed.add_field(
            name="📊 Process Info",
            value=f"PID: {process.pid}\n"
                  f"Memory: {process.memory_info().rss // (1024**2)}MB\n"
                  f"CPU: {process.cpu_percent()}%",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error getting system info: {e}")

@command("models", "List available Ollama models")
async def list_models(ctx):
    """List all available Ollama models"""
    try:
        ollama = OllamaIntegration()
        
        if not ollama.check_ollama_status():
            await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first:\n```bash\nollama serve\n```")
            return
        
        models = ollama.get_models()
        
        if not models:
            await ctx.send("📝 No models found. Pull a model first:\n```bash\nollama pull llama3.2:latest\n```")
            return
        
        embed = discord.Embed(
            title="🤖 Available Ollama Models",
            description=f"Found {len(models)} models",
            color=0x0099ff
        )
        
        for i, model in enumerate(models[:10], 1):  # Limit to 10 models
            embed.add_field(
                name=f"Model {i}",
                value=f"`{model}`",
                inline=True
            )
        
        if len(models) > 10:
            embed.set_footer(text=f"... and {len(models) - 10} more models")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error listing models: {e}")

@command("setmodel", "Set the current Ollama model")
async def set_model(ctx, *, model_name: str):
    """Set the current Ollama model"""
    try:
        ollama = OllamaIntegration()
        
        if not ollama.check_ollama_status():
            await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first:\n```bash\nollama serve\n```")
            return
        
        success = ollama.set_model(model_name)
        
        if success:
            embed = discord.Embed(
                title="✅ Model Changed",
                description=f"Successfully set model to: `{model_name}`",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Model `{model_name}` not found. Use `/models` to see available models.")
        
    except Exception as e:
        await ctx.send(f"❌ Error setting model: {e}")

@command("conversation", "Show conversation history")
async def conversation_history(ctx, limit: int = 5):
    """Show recent conversation history"""
    try:
        ollama = OllamaIntegration()
        user_id = str(ctx.author.id)
        session_id = user_id
        
        history = ollama.get_conversation_history(user_id, session_id, limit)
        
        if not history:
            await ctx.send("📝 No conversation history found.")
            return
        
        embed = discord.Embed(
            title="💬 Conversation History",
            description=f"Recent {len(history)} messages",
            color=0x3498db
        )
        
        for i, (message, response, timestamp) in enumerate(history, 1):
            embed.add_field(
                name=f"Message {i}",
                value=f"**You:** {message[:100]}{'...' if len(message) > 100 else ''}\n"
                      f"**Bot:** {response[:100]}{'...' if len(response) > 100 else ''}\n"
                      f"**Time:** {timestamp}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error getting conversation history: {e}")

@command("weather", "Get weather information for a location")
async def weather_command(ctx, *, location: str):
    """Get weather information using OpenWeatherMap API"""
    try:
        # This is a placeholder - you would need to add your OpenWeatherMap API key
        await ctx.send(f"🌤️ Weather for {location}: This feature requires an OpenWeatherMap API key.\n"
                       f"Add your API key to config.py to enable weather functionality.")
        
    except Exception as e:
        await ctx.send(f"❌ Error getting weather: {e}")

@command("code", "Generate or analyze code using AI")
async def code_command(ctx, *, prompt: str):
    """Generate or analyze code using AI"""
    try:
        ollama = OllamaIntegration()
        
        if not ollama.check_ollama_status():
            await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first:\n```bash\nollama serve\n```")
            return
        
        await ctx.send("🤔 Generating code...")
        
        # Use CodeLlama if available, otherwise use current model
        code_prompt = f"You are a helpful coding assistant. {prompt}\n\nPlease provide clean, well-commented code with explanations."
        
        user_id = str(ctx.author.id)
        session_id = f"code_{user_id}"
        
        response = ollama.chat(code_prompt, user_id, session_id)
        
        # Format response as code block
        embed = discord.Embed(
            title="💻 Code Generation",
            description=f"Response for: `{prompt}`",
            color=0x00ff7f
        )
        
        # Split response if too long
        if len(response) > 2000:
            chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
            for i, chunk in enumerate(chunks):
                embed.add_field(
                    name=f"Code Part {i+1}",
                    value=f"```\n{chunk}\n```",
                    inline=False
                )
        else:
            embed.add_field(
                name="Generated Code",
                value=f"```\n{response}\n```",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error generating code: {e}")

@command("translate", "Translate text using AI")
async def translate_command(ctx, *, text: str):
    """Translate text using AI"""
    try:
        ollama = OllamaIntegration()
        
        if not ollama.check_ollama_status():
            await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first:\n```bash\nollama serve\n```")
            return
        
        await ctx.send("🌍 Translating...")
        
        translate_prompt = f"Translate the following text to English (if not already in English) and provide the translation:\n\n{text}"
        
        user_id = str(ctx.author.id)
        session_id = f"translate_{user_id}"
        
        response = ollama.chat(translate_prompt, user_id, session_id)
        
        embed = discord.Embed(
            title="🌍 Translation",
            description=f"Original: `{text}`",
            color=0xff6b6b
        )
        embed.add_field(
            name="Translation",
            value=response,
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error translating: {e}")

@command("summarize", "Summarize text using AI")
async def summarize_command(ctx, *, text: str):
    """Summarize text using AI"""
    try:
        ollama = OllamaIntegration()
        
        if not ollama.check_ollama_status():
            await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first:\n```bash\nollama serve\n```")
            return
        
        await ctx.send("📝 Summarizing...")
        
        summarize_prompt = f"Please provide a concise summary of the following text:\n\n{text}"
        
        user_id = str(ctx.author.id)
        session_id = f"summarize_{user_id}"
        
        response = ollama.chat(summarize_prompt, user_id, session_id)
        
        embed = discord.Embed(
            title="📝 Summary",
            description=f"Original text length: {len(text)} characters",
            color=0x9b59b6
        )
        embed.add_field(
            name="Summary",
            value=response,
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error summarizing: {e}")

@command("help", "Show comprehensive help for all commands")
async def comprehensive_help(ctx):
    """Show comprehensive help for all commands"""
    embed = discord.Embed(
        title="🤖 Discord Bot with AI & RAG - Complete Help",
        description="Your AI-powered Discord bot with RAG capabilities",
        color=0x00ff00
    )
    
    # Basic Commands
    embed.add_field(
        name="🔧 Basic Commands",
        value="`/ping` - Test bot responsiveness\n"
              "`/status` - Show bot status\n"
              "`/system` - Show system information\n"
              "`/help` - Show this help",
        inline=False
    )
    
    # AI Commands
    embed.add_field(
        name="🤖 AI Commands",
        value="`/askai <question>` - Ask AI questions\n"
              "`/code <prompt>` - Generate/analyze code\n"
              "`/translate <text>` - Translate text\n"
              "`/summarize <text>` - Summarize text\n"
              "`/models` - List available models\n"
              "`/setmodel <name>` - Change AI model",
        inline=False
    )
    
    # RAG Commands
    embed.add_field(
        name="📚 RAG Commands",
        value="`/rag <query>` - RAG-powered responses\n"
              "`/ragchat <message>` - Chat with RAG context\n"
              "`/adddoc <filepath>` - Add document to knowledge base\n"
              "`/listdocs` - List documents in knowledge base\n"
              "`/ragsearch <query>` - Search knowledge base\n"
              "`/ragstats` - Show RAG system statistics",
        inline=False
    )
    
    # Utility Commands
    embed.add_field(
        name="🛠️ Utility Commands",
        value="`/conversation [limit]` - Show conversation history\n"
              "`/scrape <url>` - Add website to knowledge base\n"
              "`/createcmd <name> <desc>` - Create new command",
        inline=False
    )
    
    # MCP Commands
    embed.add_field(
        name="🔌 MCP Commands",
        value="`/listmcp` - Show available MCP servers\n"
              "`/downloadmcp <server>` - Download MCP extensions\n"
              "`/addmcp` - Add custom MCP servers",
        inline=False
    )
    
    embed.set_footer(text="Use /<command> for more information about specific commands")
    
    await ctx.send(embed=embed)
