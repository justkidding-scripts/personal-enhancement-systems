#!/usr/bin/env python3
"""
Utility and Management Commands Module
Advanced utility features including XP system, RSS feeds, goals, and Discord CLI integration
"""

import discord
from discord.ext import commands, tasks
from command_manager import command
import asyncio
import os
import sys
import json
import subprocess
import tempfile
import feedparser
import requests
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import random

# Add ollama integration to path
sys.path.append(str(Path(__file__).parent.parent / "ollama_integration"))
from ollama_integration import OllamaIntegration

# Initialize systems
ollama = OllamaIntegration()

# Database setup for XP and goals
DB_PATH = Path(__file__).parent.parent / "bot_data.db"
RSS_FEEDS_FILE = Path(__file__).parent.parent / "rss_feeds.json"

def init_database():
    """Initialize SQLite database for XP and goals"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # XP System table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_xp (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            last_daily TIMESTAMP,
            total_messages INTEGER DEFAULT 0
        )
    ''')
    
    # Goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            goal TEXT,
            reward TEXT,
            deadline TIMESTAMP,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            progress TEXT DEFAULT '0'
        )
    ''')
    
    # RSS feeds table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rss_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_name TEXT,
            title TEXT,
            link TEXT UNIQUE,
            published TIMESTAMP,
            content TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on module load
init_database()

# XP System
XP_PER_MESSAGE = 5
XP_PER_LEVEL = 100
DAILY_BONUS_XP = 50

# RSS Feeds configuration
RSS_FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "AP News": "https://rsshub.app/ap/topics/apf-topnews",
    "NPR": "https://feeds.npr.org/1001/rss.xml",
    "Guardian": "https://www.theguardian.com/world/rss"
}

@command("xp", "Check your XP and level")
async def check_xp(ctx, user: discord.Member = None):
    """
    Check XP and level for yourself or another user
    Usage: /xp [user]
    """
    target_user = user or ctx.author
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_xp WHERE user_id = ?", (str(target_user.id),))
    result = cursor.fetchone()
    
    if not result:
        # Create new user entry
        cursor.execute(
            "INSERT INTO user_xp (user_id, username, xp, level) VALUES (?, ?, ?, ?)",
            (str(target_user.id), target_user.name, 0, 1)
        )
        conn.commit()
        xp, level, total_messages = 0, 1, 0
    else:
        xp, level, total_messages = result[2], result[3], result[5]
    
    conn.close()
    
    # Calculate progress to next level
    current_level_xp = level * XP_PER_LEVEL
    next_level_xp = (level + 1) * XP_PER_LEVEL
    progress = xp - current_level_xp
    needed = next_level_xp - xp
    
    embed = discord.Embed(
        title=f"📊 XP Status - {target_user.display_name}",
        color=0x00ff7f,
        timestamp=datetime.now()
    )
    
    embed.add_field(name="🏆 Level", value=str(level), inline=True)
    embed.add_field(name="⭐ Total XP", value=f"{xp:,}", inline=True)
    embed.add_field(name="💬 Messages", value=f"{total_messages:,}", inline=True)
    
    embed.add_field(
        name="📈 Progress to Next Level",
        value=f"{progress}/{XP_PER_LEVEL} XP\n{needed} XP needed",
        inline=False
    )
    
    # Progress bar
    progress_percent = (progress / XP_PER_LEVEL) * 100
    bar_length = 20
    filled = int((progress_percent / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    embed.add_field(name="Progress Bar", value=f"`{bar}` {progress_percent:.1f}%", inline=False)
    
    embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else None)
    
    await ctx.send(embed=embed)

@command("leaderboard", "Show XP leaderboard")
async def leaderboard(ctx, limit: int = 10):
    """
    Show server XP leaderboard
    Usage: /leaderboard [limit]
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, username, xp, level FROM user_xp ORDER BY xp DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        await ctx.send("📊 No XP data found yet!")
        return
    
    embed = discord.Embed(
        title="🏆 XP Leaderboard",
        description=f"Top {len(results)} users by XP",
        color=0xf1c40f,
        timestamp=datetime.now()
    )
    
    leaderboard_text = ""
    for i, (user_id, username, xp, level) in enumerate(results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text += f"{medal} **{username}** - Level {level} ({xp:,} XP)\n"
    
    embed.add_field(name="Rankings", value=leaderboard_text, inline=False)
    embed.set_footer(text="💬 Earn XP by chatting and completing daily bonuses!")
    
    await ctx.send(embed=embed)

@command("daily", "Claim daily XP bonus")
async def daily_bonus(ctx):
    """
    Claim daily XP bonus
    Usage: /daily
    """
    user_id = str(ctx.author.id)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT last_daily FROM user_xp WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result and result[0]:
        last_daily = datetime.fromisoformat(result[0])
        if datetime.now() - last_daily < timedelta(days=1):
            next_daily = last_daily + timedelta(days=1)
            await ctx.send(f"⏰ Daily bonus already claimed! Next bonus available: {next_daily.strftime('%H:%M:%S')}")
            conn.close()
            return
    
    # Award daily bonus
    cursor.execute(
        "UPDATE user_xp SET xp = xp + ?, last_daily = ? WHERE user_id = ?",
        (DAILY_BONUS_XP, datetime.now().isoformat(), user_id)
    )
    
    if cursor.rowcount == 0:
        # Create new user
        cursor.execute(
            "INSERT INTO user_xp (user_id, username, xp, level, last_daily) VALUES (?, ?, ?, ?, ?)",
            (user_id, ctx.author.name, DAILY_BONUS_XP, 1, datetime.now().isoformat())
        )
    
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="🎁 Daily Bonus Claimed!",
        description=f"You earned **{DAILY_BONUS_XP} XP**!",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.add_field(name="Next Bonus", value="Available in 24 hours", inline=False)
    embed.set_footer(text="💡 Come back tomorrow for another bonus!")
    
    await ctx.send(embed=embed)

@command("goalfam", "Set a personal goal")
async def set_goal(ctx, deadline: str, reward: str, *, goal: str):
    """
    Set a personal goal with deadline and reward
    Usage: /goalfam <deadline> <reward> <goal>
    Example: /goalfam 2025-12-31 "New laptop" Learn Python programming
    """
    try:
        # Parse deadline
        deadline_dt = datetime.strptime(deadline, "%Y-%m-%d")
        
        if deadline_dt <= datetime.now():
            await ctx.send("❌ Deadline must be in the future!")
            return
        
        # Save goal to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO user_goals (user_id, goal, reward, deadline) VALUES (?, ?, ?, ?)",
            (str(ctx.author.id), goal, reward, deadline_dt.isoformat())
        )
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🎯 Goal Set Successfully!",
            description=f"**Goal:** {goal}\n**Reward:** {reward}\n**Deadline:** {deadline}",
            color=0x00ff7f,
            timestamp=datetime.now()
        )
        embed.add_field(name="Goal ID", value=str(goal_id), inline=True)
        embed.add_field(name="Days Left", value=str((deadline_dt - datetime.now()).days), inline=True)
        embed.set_footer(text="Use /mygoals to track progress!")
        
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send("❌ Invalid date format! Use YYYY-MM-DD (e.g., 2025-12-31)")
    except Exception as e:
        await ctx.send(f"❌ Error setting goal: {e}")

@command("mygoals", "View your goals")
async def my_goals(ctx):
    """
    View all your goals and progress
    Usage: /mygoals
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, goal, reward, deadline, completed, progress FROM user_goals WHERE user_id = ? ORDER BY deadline",
        (str(ctx.author.id),)
    )
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        await ctx.send("🎯 No goals set yet! Use `/goalfam` to create your first goal.")
        return
    
    embed = discord.Embed(
        title="🎯 Your Goals",
        description=f"You have {len(results)} goals",
        color=0x3498db,
        timestamp=datetime.now()
    )
    
    for goal_id, goal, reward, deadline, completed, progress in results:
        deadline_dt = datetime.fromisoformat(deadline)
        days_left = (deadline_dt - datetime.now()).days
        
        status = "✅ Completed" if completed else f"⏰ {days_left} days left"
        if days_left < 0 and not completed:
            status = "❌ Overdue"
        
        embed.add_field(
            name=f"Goal #{goal_id}",
            value=f"**Goal:** {goal}\n**Reward:** {reward}\n**Status:** {status}\n**Progress:** {progress}%",
            inline=False
        )
    
    embed.set_footer(text="Use /updategoal <id> <progress> to update progress")
    
    await ctx.send(embed=embed)

@command("updategoal", "Update goal progress")
async def update_goal(ctx, goal_id: int, progress: str):
    """
    Update progress on a goal
    Usage: /updategoal <goal_id> <progress>
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE user_goals SET progress = ? WHERE id = ? AND user_id = ?",
        (progress, goal_id, str(ctx.author.id))
    )
    
    if cursor.rowcount == 0:
        await ctx.send("❌ Goal not found or you don't own this goal!")
        conn.close()
        return
    
    # Check if goal is completed (100%)
    if progress == "100":
        cursor.execute(
            "UPDATE user_goals SET completed = TRUE WHERE id = ?",
            (goal_id,)
        )
        
        # Get goal details for celebration
        cursor.execute(
            "SELECT goal, reward FROM user_goals WHERE id = ?",
            (goal_id,)
        )
        goal_data = cursor.fetchone()
        
        embed = discord.Embed(
            title="🎉 Goal Completed!",
            description=f"**Congratulations!** You completed your goal!\n\n"
                       f"**Goal:** {goal_data[0]}\n"
                       f"**Your Reward:** {goal_data[1]}\n\n"
                       f"Time to celebrate! 🎊",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.set_footer(text="🏆 Achievement unlocked!")
        
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="📈 Goal Progress Updated",
            description=f"Goal #{goal_id} progress updated to **{progress}%**",
            color=0x00ff7f,
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    
    conn.commit()
    conn.close()

@command("channelexport", "Export entire channel as text")
async def channel_export(ctx, limit: int = 1000):
    """
    Export entire channel history as text file
    Usage: /channelexport [limit]
    """
    await ctx.send(f"📤 Exporting channel history (last {limit} messages)...")
    
    try:
        messages = []
        async for message in ctx.channel.history(limit=limit):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = message.author.display_name
            content = message.content or "[No text content]"
            
            # Handle attachments
            if message.attachments:
                attachments = ", ".join([att.filename for att in message.attachments])
                content += f" [Attachments: {attachments}]"
            
            messages.append(f"[{timestamp}] {author}: {content}")
        
        # Reverse to get chronological order
        messages.reverse()
        
        # Create export file
        export_content = f"Channel Export: #{ctx.channel.name}\n"
        export_content += f"Server: {ctx.guild.name}\n"
        export_content += f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_content += f"Messages: {len(messages)}\n"
        export_content += "=" * 50 + "\n\n"
        export_content += "\n".join(messages)
        
        # Save to file
        filename = f"channel_export_{ctx.channel.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = Path(__file__).parent.parent / "exports" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(export_content)
        
        # Send file
        embed = discord.Embed(
            title="📤 Channel Export Complete",
            description=f"Exported {len(messages)} messages from #{ctx.channel.name}",
            color=0x00ff7f,
            timestamp=datetime.now()
        )
        
        await ctx.send(embed=embed, file=discord.File(filepath))
        
    except Exception as e:
        await ctx.send(f"❌ Error exporting channel: {e}")

@command("wipemyass", "Delete your messages from today")
async def wipe_my_messages(ctx):
    """
    Delete all your messages from today in current channel
    Usage: /wipemyass
    """
    # Confirmation
    embed = discord.Embed(
        title="⚠️ Confirm Message Deletion",
        description="This will delete ALL your messages from today in this channel.\n\n"
                   "**This action cannot be undone!**\n\n"
                   "React with ✅ to confirm or ❌ to cancel.",
        color=0xff9900,
        timestamp=datetime.now()
    )
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id
    
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        if str(reaction.emoji) == "❌":
            await ctx.send("❌ Message deletion cancelled.")
            return
        
        # Delete messages from today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        deleted_count = 0
        
        await ctx.send("🗑️ Deleting your messages from today...")
        
        async for message in ctx.channel.history(after=today):
            if message.author == ctx.author:
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.5)  # Rate limiting
                except discord.errors.NotFound:
                    pass  # Message already deleted
                except discord.errors.Forbidden:
                    await ctx.send("❌ I don't have permission to delete messages!")
                    return
        
        embed = discord.Embed(
            title="🗑️ Messages Deleted",
            description=f"Successfully deleted **{deleted_count}** of your messages from today.",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
        
    except asyncio.TimeoutError:
        await ctx.send("⏰ Confirmation timeout. Message deletion cancelled.")

@command("rss", "Get latest news from RSS feeds")
async def rss_news(ctx, feed_name: str = "all"):
    """
    Get latest news from RSS feeds
    Usage: /rss [feed_name]
    Available feeds: BBC, Reuters, AP, NPR, Guardian
    """
    await ctx.send("📰 Fetching latest news...")
    
    try:
        if feed_name.lower() == "all":
            feeds_to_check = RSS_FEEDS.items()
        else:
            feed_name_proper = None
            for name in RSS_FEEDS.keys():
                if name.lower() == feed_name.lower():
                    feed_name_proper = name
                    break
            
            if not feed_name_proper:
                available = ", ".join(RSS_FEEDS.keys())
                await ctx.send(f"❌ Unknown feed. Available: {available}")
                return
            
            feeds_to_check = [(feed_name_proper, RSS_FEEDS[feed_name_proper])]
        
        all_articles = []
        
        for name, url in feeds_to_check:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:  # Top 3 from each feed
                    all_articles.append({
                        "source": name,
                        "title": entry.title,
                        "link": entry.link,
                        "published": getattr(entry, 'published', 'Unknown'),
                        "summary": getattr(entry, 'summary', '')[:200]
                    })
            except Exception as e:
                print(f"Error fetching {name}: {e}")
        
        if not all_articles:
            await ctx.send("❌ No articles found!")
            return
        
        # Sort by source and limit
        all_articles = all_articles[:10]
        
        embed = discord.Embed(
            title="📰 Latest News",
            description=f"Top news from {feed_name if feed_name != 'all' else 'multiple sources'}",
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        for article in all_articles:
            embed.add_field(
                name=f"📰 {article['source']}",
                value=f"**[{article['title']}]({article['link']})**\n"
                      f"{article['summary']}...\n"
                      f"*{article['published']}*",
                inline=False
            )
        
        embed.set_footer(text="📡 RSS News Feed")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error fetching news: {e}")

@command("imagine", "Generate AI images (placeholder)")
async def imagine_image(ctx, *, prompt: str):
    """
    Generate AI images (placeholder for future implementation)
    Usage: /imagine <prompt>
    """
    embed = discord.Embed(
        title="🎨 AI Image Generation",
        description=f"**Prompt:** {prompt}\n\n"
                   f"🚧 **Coming Soon!** 🚧\n\n"
                   f"AI image generation will be available soon.\n"
                   f"This will integrate with:\n"
                   f"• Stable Diffusion\n"
                   f"• DALL-E API\n"
                   f"• Local image models\n\n"
                   f"Stay tuned for updates!",
        color=0xff6b6b,
        timestamp=datetime.now()
    )
    embed.set_footer(text="🎨 AI Art Generation - Coming Soon")
    
    await ctx.send(embed=embed)

# RSS Feed Task (runs 3 times daily)
@tasks.loop(hours=8)  # Every 8 hours = 3 times per day
async def rss_feed_task():
    """Automatically fetch and store RSS feeds"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for feed_name, feed_url in RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Top 5 from each feed
                    # Check if already stored
                    cursor.execute("SELECT id FROM rss_posts WHERE link = ?", (entry.link,))
                    if cursor.fetchone():
                        continue
                    
                    # Store new article
                    cursor.execute(
                        "INSERT INTO rss_posts (feed_name, title, link, published, content) VALUES (?, ?, ?, ?, ?)",
                        (feed_name, entry.title, entry.link, 
                         getattr(entry, 'published', datetime.now().isoformat()),
                         getattr(entry, 'summary', ''))
                    )
            except Exception as e:
                print(f"RSS Error for {feed_name}: {e}")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"RSS Task Error: {e}")

# XP System Event Listener
@commands.Cog.listener()
async def on_message(message):
    """Award XP for messages"""
    if message.author.bot:
        return
    
    user_id = str(message.author.id)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT xp, level, total_messages FROM user_xp WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        current_xp, current_level, total_messages = result
        new_xp = current_xp + XP_PER_MESSAGE
        new_messages = total_messages + 1
        
        # Check for level up
        new_level = new_xp // XP_PER_LEVEL + 1
        
        cursor.execute(
            "UPDATE user_xp SET xp = ?, level = ?, total_messages = ?, username = ? WHERE user_id = ?",
            (new_xp, new_level, new_messages, message.author.name, user_id)
        )
        
        # Level up notification
        if new_level > current_level:
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"**{message.author.display_name}** reached level **{new_level}**!",
                color=0xf1c40f
            )
            embed.add_field(name="Total XP", value=f"{new_xp:,}", inline=True)
            embed.add_field(name="Messages", value=f"{new_messages:,}", inline=True)
            
            await message.channel.send(embed=embed)
    else:
        # Create new user
        cursor.execute(
            "INSERT INTO user_xp (user_id, username, xp, level, total_messages) VALUES (?, ?, ?, ?, ?)",
            (user_id, message.author.name, XP_PER_MESSAGE, 1, 1)
        )
    
    conn.commit()
    conn.close()

# Start RSS task when bot is ready
@commands.Cog.listener()
async def on_ready():
    """Start RSS feed task when bot is ready"""
    if not rss_feed_task.is_running():
        rss_feed_task.start()

