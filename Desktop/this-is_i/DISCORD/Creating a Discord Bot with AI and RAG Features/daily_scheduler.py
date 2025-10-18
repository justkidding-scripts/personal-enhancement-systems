#!/usr/bin/env python3
"""
Daily Scheduler Module
Handles scheduled tasks like daily reflection prompts, RSS feeds, and XP bonuses
"""

import asyncio
import discord
from discord.ext import tasks
from datetime import datetime, time, timezone, timedelta
import json
import os
import sys
from pathlib import Path
import feedparser
import sqlite3
from typing import Dict, List, Optional

# Add modules to path
sys.path.append(str(Path(__file__).parent / "ollama_integration"))
from ollama_integration import OllamaIntegration

# Initialize systems
ollama = OllamaIntegration()

# Configuration
SCHEDULER_DB = Path(__file__).parent / "scheduler.db"
RAG_DATA_FOLDER = Path(__file__).parent / "rag_data"

# RSS Sources (unbiased news)
RSS_SOURCES = [
    {
        "name": "BBC News",
        "url": "http://feeds.bbci.co.uk/news/rss.xml",
        "category": "general"
    },
    {
        "name": "Reuters",
        "url": "http://feeds.reuters.com/reuters/topNews",
        "category": "general"
    },
    {
        "name": "AP News",
        "url": "https://feeds.apnews.com/rss/apf-topnews",
        "category": "general"
    },
    {
        "name": "NPR",
        "url": "https://feeds.npr.org/1001/rss.xml",
        "category": "general"
    },
    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/world/rss",
        "category": "world"
    }
]

class DailyScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.init_database()
        
    def init_database(self):
        """Initialize scheduler database"""
        conn = sqlite3.connect(SCHEDULER_DB)
        cursor = conn.cursor()
        
        # Scheduled tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER,
                schedule_time TEXT,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily reflections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                question TEXT NOT NULL,
                response TEXT,
                ai_analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RSS cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                published TEXT,
                summary TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_scheduled_task(self, task_type: str, user_id: int, channel_id: int, guild_id: int, schedule_time: str = "16:00"):
        """Add a scheduled task"""
        conn = sqlite3.connect(SCHEDULER_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_tasks (task_type, user_id, channel_id, guild_id, schedule_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (task_type, user_id, channel_id, guild_id, schedule_time))
        
        conn.commit()
        conn.close()
    
    def get_scheduled_tasks(self, task_type: str = None) -> List[Dict]:
        """Get scheduled tasks"""
        conn = sqlite3.connect(SCHEDULER_DB)
        cursor = conn.cursor()
        
        if task_type:
            cursor.execute('''
                SELECT * FROM scheduled_tasks 
                WHERE task_type = ? AND enabled = 1
            ''', (task_type,))
        else:
            cursor.execute('SELECT * FROM scheduled_tasks WHERE enabled = 1')
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'task_type': row[1],
                'user_id': row[2],
                'channel_id': row[3],
                'guild_id': row[4],
                'schedule_time': row[5],
                'enabled': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return tasks
    
    def save_daily_reflection(self, user_id: int, question: str, response: str = None, ai_analysis: str = None):
        """Save daily reflection data"""
        conn = sqlite3.connect(SCHEDULER_DB)
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_reflections 
            (user_id, date, question, response, ai_analysis)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, today, question, response, ai_analysis))
        
        conn.commit()
        conn.close()
        
        # Also save to RAG system
        if response:
            self.save_to_rag(user_id, question, response, ai_analysis)
    
    def save_to_rag(self, user_id: int, question: str, response: str, ai_analysis: str = None):
        """Save reflection data to RAG system"""
        try:
            # Create user-specific reflection file
            if not RAG_DATA_FOLDER.exists():
                RAG_DATA_FOLDER.mkdir(parents=True)
            
            reflection_file = RAG_DATA_FOLDER / f"user_{user_id}_reflections.txt"
            
            with open(reflection_file, 'a', encoding='utf-8') as f:
                f.write(f"\n--- Daily Reflection {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n")
                f.write(f"Question: {question}\n")
                f.write(f"Response: {response}\n")
                if ai_analysis:
                    f.write(f"AI Analysis: {ai_analysis}\n")
                f.write("---\n\n")
            
            # Add to RAG system
            from rag_system import RAGSystem
            rag = RAGSystem()
            rag.add_document(reflection_file)
            
        except Exception as e:
            print(f"Error saving to RAG: {e}")
    
    def get_user_reflections(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get user's recent reflections"""
        conn = sqlite3.connect(SCHEDULER_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM daily_reflections 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, days))
        
        reflections = []
        for row in cursor.fetchall():
            reflections.append({
                'id': row[0],
                'user_id': row[1],
                'date': row[2],
                'question': row[3],
                'response': row[4],
                'ai_analysis': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return reflections
    
    async def send_daily_reflection_prompt(self, user_id: int, channel_id: int):
        """Send daily reflection prompt to user"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                return False
            
            user = self.bot.get_user(user_id)
            if not user:
                return False
            
            # Create reflection prompt
            embed = discord.Embed(
                title="🤔 Daily Reflection Time",
                description=f"Good evening, {user.mention}!\n\n"
                           "It's time for your daily reflection.\n\n"
                           "**Today's Question:**\n"
                           "**What is important today?**\n\n"
                           "Take a moment to think about:\n"
                           "• What mattered most to you today?\n"
                           "• What did you learn or accomplish?\n"
                           "• What are you grateful for?\n"
                           "• What would you like to focus on tomorrow?",
                color=0x3498db,
                timestamp=datetime.now()
            )
            
            embed.set_footer(text="Your response will be saved for AI analysis • Reply with your thoughts")
            
            # Save the question
            question = "What is important today?"
            self.save_daily_reflection(user_id, question)
            
            await channel.send(embed=embed)
            
            # Wait for user response (with timeout)
            def check(message):
                return message.author.id == user_id and message.channel.id == channel_id
            
            try:
                response_msg = await self.bot.wait_for('message', timeout=1800, check=check)  # 30 minutes
                
                # Get AI analysis of the response
                if ollama.check_ollama_status():
                    ai_prompt = f"""
                    Analyze this daily reflection response and provide insights:
                    
                    Question: {question}
                    Response: {response_msg.content}
                    
                    Please provide:
                    1. Key themes and patterns
                    2. Emotional tone analysis
                    3. Growth opportunities
                    4. Encouraging insights
                    
                    Keep it supportive and constructive.
                    """
                    
                    ai_analysis = ollama.chat(ai_prompt, user_id=str(user_id), session_id="daily_reflection")
                    
                    # Save the response and analysis
                    self.save_daily_reflection(user_id, question, response_msg.content, ai_analysis)
                    
                    # Send AI analysis
                    analysis_embed = discord.Embed(
                        title="🤖 AI Reflection Analysis",
                        description=ai_analysis,
                        color=0x00ff7f,
                        timestamp=datetime.now()
                    )
                    
                    analysis_embed.set_footer(text="Your reflection has been saved • Use /compileme to see insights")
                    
                    await channel.send(embed=analysis_embed)
                else:
                    # Save without AI analysis
                    self.save_daily_reflection(user_id, question, response_msg.content)
                    
                    await channel.send("✅ Your reflection has been saved! Use `/compileme` to get AI insights.")
                
                return True
                
            except asyncio.TimeoutError:
                await channel.send("⏰ Reflection time expired. You can still share your thoughts anytime!")
                return False
                
        except Exception as e:
            print(f"Error sending daily reflection: {e}")
            return False
    
    async def fetch_and_send_rss_news(self, channel_id: int):
        """Fetch and send RSS news updates"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                return False
            
            # Fetch news from all sources
            all_articles = []
            
            for source in RSS_SOURCES:
                try:
                    feed = feedparser.parse(source['url'])
                    
                    for entry in feed.entries[:3]:  # Top 3 from each source
                        all_articles.append({
                            'source': source['name'],
                            'title': entry.title,
                            'link': entry.link,
                            'published': getattr(entry, 'published', 'Unknown'),
                            'summary': getattr(entry, 'summary', '')[:200] + '...' if len(getattr(entry, 'summary', '')) > 200 else getattr(entry, 'summary', '')
                        })
                        
                except Exception as e:
                    print(f"Error fetching from {source['name']}: {e}")
                    continue
            
            if not all_articles:
                return False
            
            # Sort by recency and take top 10
            all_articles = all_articles[:10]
            
            # Create news embed
            embed = discord.Embed(
                title="📰 Daily News Update",
                description=f"Latest news from {len(RSS_SOURCES)} unbiased sources",
                color=0xe74c3c,
                timestamp=datetime.now()
            )
            
            for i, article in enumerate(all_articles[:5], 1):  # Show top 5
                embed.add_field(
                    name=f"{i}. {article['source']}",
                    value=f"**[{article['title']}]({article['link']})**\n"
                          f"{article['summary']}\n"
                          f"*Published: {article['published']}*",
                    inline=False
                )
            
            embed.set_footer(text=f"📊 {len(all_articles)} articles • Next update in 8 hours")
            
            await channel.send(embed=embed)
            
            # Cache articles
            self.cache_rss_articles(all_articles)
            
            return True
            
        except Exception as e:
            print(f"Error sending RSS news: {e}")
            return False
    
    def cache_rss_articles(self, articles: List[Dict]):
        """Cache RSS articles in database"""
        conn = sqlite3.connect(SCHEDULER_DB)
        cursor = conn.cursor()
        
        for article in articles:
            cursor.execute('''
                INSERT OR IGNORE INTO rss_cache 
                (source_name, title, link, published, summary)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                article['source'],
                article['title'],
                article['link'],
                article['published'],
                article['summary']
            ))
        
        # Clean old cache (keep last 1000 articles)
        cursor.execute('''
            DELETE FROM rss_cache 
            WHERE id NOT IN (
                SELECT id FROM rss_cache 
                ORDER BY cached_at DESC 
                LIMIT 1000
            )
        ''')
        
        conn.commit()
        conn.close()

# Global scheduler instance
scheduler = None

async def configure_scheduler(bot, user_id: int, channel_id: int, task_type: str):
    """Configure scheduler for specific tasks"""
    global scheduler
    
    if not scheduler:
        scheduler = DailyScheduler(bot)
    
    guild_id = bot.get_channel(channel_id).guild.id if bot.get_channel(channel_id) else 0
    
    if task_type == "daily" or task_type == "all":
        scheduler.add_scheduled_task("daily_reflection", user_id, channel_id, guild_id, "16:00")
    
    if task_type == "rss" or task_type == "all":
        scheduler.add_scheduled_task("rss_news", user_id, channel_id, guild_id, "08:00")
        scheduler.add_scheduled_task("rss_news", user_id, channel_id, guild_id, "16:00")
        scheduler.add_scheduled_task("rss_news", user_id, channel_id, guild_id, "00:00")
    
    # Start the scheduler loop if not already running
    if not daily_scheduler_loop.is_running():
        daily_scheduler_loop.start()

async def trigger_daily_reflection(bot, channel_id: int, user_id: int):
    """Manually trigger daily reflection"""
    global scheduler
    
    if not scheduler:
        scheduler = DailyScheduler(bot)
    
    return await scheduler.send_daily_reflection_prompt(user_id, channel_id)

@tasks.loop(minutes=1)  # Check every minute
async def daily_scheduler_loop():
    """Main scheduler loop"""
    global scheduler
    
    if not scheduler:
        return
    
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    # Get all scheduled tasks for current time
    tasks = scheduler.get_scheduled_tasks()
    
    for task in tasks:
        if task['schedule_time'] == current_time:
            try:
                if task['task_type'] == "daily_reflection":
                    await scheduler.send_daily_reflection_prompt(
                        task['user_id'], 
                        task['channel_id']
                    )
                
                elif task['task_type'] == "rss_news":
                    await scheduler.fetch_and_send_rss_news(task['channel_id'])
                
            except Exception as e:
                print(f"Error executing scheduled task {task['task_type']}: {e}")

@daily_scheduler_loop.before_loop
async def before_scheduler():
    """Wait for bot to be ready before starting scheduler"""
    if scheduler and scheduler.bot:
        await scheduler.bot.wait_until_ready()

# Initialize when imported
def init_scheduler(bot):
    """Initialize scheduler with bot instance"""
    global scheduler
    scheduler = DailyScheduler(bot)
    return scheduler