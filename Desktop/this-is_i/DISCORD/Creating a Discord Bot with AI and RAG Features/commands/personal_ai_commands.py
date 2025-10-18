#!/usr/bin/env python3
"""
Personal AI Commands Module
Advanced personal AI features for daily reflection, creativity, and continuous conversation
"""

import discord
from discord.ext import commands, tasks
from command_manager import command
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, time
import json
import aiofiles

# Add ollama integration to path
sys.path.append(str(Path(__file__).parent.parent / "ollama_integration"))
from ollama_integration import OllamaIntegration

# Add RAG system to path
sys.path.append(str(Path(__file__).parent.parent))
from rag_system import RAGSystem

# Initialize systems
ollama = OllamaIntegration()
rag_system = RAGSystem()

# Personal data storage
PERSONAL_DATA_DIR = Path(__file__).parent.parent / "personal_data"
PERSONAL_DATA_DIR.mkdir(exist_ok=True)

# Daily reflection storage
REFLECTION_FILE = PERSONAL_DATA_DIR / "daily_reflections.jsonl"
CONVERSATIONS_DIR = PERSONAL_DATA_DIR / "conversations"
CONVERSATIONS_DIR.mkdir(exist_ok=True)

# Global conversation states
active_conversations = {}
continuous_conversations = {}

@command("whatisimportant", "Daily reflection prompt - What is important today?")
async def daily_reflection(ctx, *, response: str = None):
    """
    Daily reflection command - What is important?
    Usage: /whatisimportant <your thoughts>
    """
    if not response:
        embed = discord.Embed(
            title="🤔 Daily Reflection",
            description="What is important to you today?",
            color=0x3498db,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="How to use",
            value="Type: `/whatisimportant <your thoughts>`",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Store the reflection
    reflection_data = {
        "timestamp": datetime.now().isoformat(),
        "user_id": str(ctx.author.id),
        "username": ctx.author.name,
        "reflection": response,
        "channel": ctx.channel.name
    }
    
    # Save to JSONL file
    async with aiofiles.open(REFLECTION_FILE, 'a', encoding='utf-8') as f:
        await f.write(json.dumps(reflection_data) + '\n')
    
    # Also save to RAG system
    rag_file = Path(__file__).parent.parent / "rag_documents" / f"reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    async with aiofiles.open(rag_file, 'w', encoding='utf-8') as f:
        await f.write(f"Daily Reflection - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        await f.write(f"User: {ctx.author.name}\n")
        await f.write(f"What is important: {response}\n")
    
    # Add to RAG system
    try:
        rag_system.add_document(rag_file)
    except Exception as e:
        print(f"Error adding reflection to RAG: {e}")
    
    # Get Ollama response
    if ollama.check_ollama_status():
        await ctx.send("🤔 Reflecting on your thoughts...")
        
        prompt = f"""You are a wise AI companion helping with daily reflection. The user shared what's important to them today: "{response}"

        Provide a thoughtful, encouraging response that:
        1. Acknowledges their priorities
        2. Offers gentle insights or questions for deeper reflection
        3. Connects to themes of growth and meaning
        4. Is warm and supportive

        Keep it concise but meaningful."""
        
        try:
            ai_response = ollama.chat(prompt, str(ctx.author.id), f"reflection_{datetime.now().date()}")
            
            embed = discord.Embed(
                title="💭 AI Reflection",
                description=ai_response,
                color=0x00ff7f,
                timestamp=datetime.now()
            )
            embed.add_field(name="Your Reflection", value=response[:500], inline=False)
            embed.set_footer(text="Reflection saved to personal data & RAG system")
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error getting AI reflection: {e}")
    else:
        embed = discord.Embed(
            title="✅ Reflection Saved",
            description="Your reflection has been saved to your personal data.",
            color=0x00ff00
        )
        embed.add_field(name="Your Reflection", value=response[:500], inline=False)
        await ctx.send(embed=embed)

@command("compileme", "Get AI insights on your reflection data")
async def compile_me(ctx):
    """
    Compile and analyze your reflection data
    Usage: /compileme
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first.")
        return
    
    await ctx.send("📊 Analyzing your reflection data...")
    
    try:
        # Read reflection data
        reflections = []
        if REFLECTION_FILE.exists():
            async with aiofiles.open(REFLECTION_FILE, 'r', encoding='utf-8') as f:
                async for line in f:
                    if line.strip():
                        reflections.append(json.loads(line))
        
        if not reflections:
            await ctx.send("📝 No reflection data found. Use `/whatisimportant` to start building your reflection history!")
            return
        
        # Filter reflections for this user
        user_reflections = [r for r in reflections if r['user_id'] == str(ctx.author.id)]
        
        if not user_reflections:
            await ctx.send("📝 No personal reflections found for you yet!")
            return
        
        # Prepare data for analysis
        reflection_text = "\n".join([
            f"Date: {r['timestamp'][:10]} - {r['reflection']}" 
            for r in user_reflections[-10:]  # Last 10 reflections
        ])
        
        prompt = f"""Analyze these personal reflections and provide insights:

{reflection_text}

As an AI companion, provide:
1. Key themes and patterns you notice
2. Areas of growth or change over time
3. Strengths and values that emerge
4. Gentle suggestions for continued development
5. A brief encouraging summary

Be insightful, supportive, and personal in your analysis."""
        
        ai_response = ollama.chat(prompt, str(ctx.author.id), "compile_analysis")
        
        embed = discord.Embed(
            title="📊 Your Personal Compilation",
            description=ai_response,
            color=0x9b59b6,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📈 Data Points",
            value=f"Analyzed {len(user_reflections)} reflections",
            inline=True
        )
        embed.add_field(
            name="📅 Time Span",
            value=f"From {user_reflections[0]['timestamp'][:10]} to {user_reflections[-1]['timestamp'][:10]}",
            inline=True
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error compiling data: {e}")

@command("creativeai", "Get creative suggestions based on your knowledge")
async def creative_ai(ctx):
    """
    Get creative project suggestions based on your personal data
    Usage: /creativeai
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first.")
        return
    
    await ctx.send("🎨 Generating creative ideas based on your knowledge...")
    
    try:
        # Search RAG system for user's data
        search_results = rag_system.search_documents(f"user {ctx.author.name} reflection important", limit=5)
        
        context = ""
        if search_results:
            context = "\n".join([result['content'][:200] for result in search_results])
        
        prompt = f"""Based on this person's reflections and interests, suggest creative projects they could make or create:

Context about the user:
{context}

Provide 3-5 specific, actionable creative project ideas that:
1. Align with their interests and values
2. Are achievable and inspiring
3. Could lead to personal growth or impact
4. Range from simple to ambitious

Be creative, practical, and encouraging!"""
        
        ai_response = ollama.chat(prompt, str(ctx.author.id), "creative_suggestions")
        
        embed = discord.Embed(
            title="🎨 Creative AI Suggestions",
            description=ai_response,
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        embed.set_footer(text="Based on your personal reflection data")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error generating creative ideas: {e}")

@command("greedisgood", "Daily wealth-building suggestion")
async def greed_is_good(ctx):
    """
    Get a daily wealth-building suggestion based on your profile
    Usage: /greedisgood
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first.")
        return
    
    await ctx.send("💰 Analyzing wealth-building opportunities...")
    
    try:
        # Get user context from RAG
        search_results = rag_system.search_documents(f"user {ctx.author.name}", limit=3)
        context = "\n".join([result['content'][:150] for result in search_results]) if search_results else ""
        
        prompt = f"""Based on this person's profile and interests, suggest ONE specific, actionable thing they could do TODAY to build wealth or improve their financial situation:

User context:
{context}

Provide:
1. One specific action they can take today
2. Why it aligns with their profile/interests
3. Potential impact and timeline
4. Next steps to get started

Be practical, ethical, and motivating. Focus on real wealth-building strategies."""
        
        ai_response = ollama.chat(prompt, str(ctx.author.id), "wealth_building")
        
        embed = discord.Embed(
            title="💰 Daily Wealth Builder",
            description=ai_response,
            color=0xf1c40f,
            timestamp=datetime.now()
        )
        embed.set_footer(text="💡 Greed is good when it drives growth!")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error generating wealth suggestion: {e}")

@command("lifeofmeaning", "Get insights for a meaningful life")
async def life_of_meaning(ctx):
    """
    Get AI insights for living a meaningful life
    Usage: /lifeofmeaning
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first.")
        return
    
    await ctx.send("🌟 Contemplating the meaning of life...")
    
    try:
        # Get user's reflection data for context
        search_results = rag_system.search_documents(f"reflection important {ctx.author.name}", limit=5)
        context = "\n".join([result['content'][:200] for result in search_results]) if search_results else ""
        
        prompt = f"""Based on this person's reflections and what they find important, provide insights for living a meaningful life:

Their reflections and values:
{context}

Provide thoughtful insights on:
1. How to align daily actions with deeper purpose
2. Ways to create lasting impact and fulfillment
3. Practices for cultivating meaning and growth
4. Perspectives on what makes life truly worthwhile

Be philosophical, wise, and personally relevant."""
        
        ai_response = ollama.chat(prompt, str(ctx.author.id), "meaning_of_life")
        
        embed = discord.Embed(
            title="🌟 Life of Meaning",
            description=ai_response,
            color=0x8e44ad,
            timestamp=datetime.now()
        )
        embed.set_footer(text="✨ The unexamined life is not worth living - Socrates")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error generating life insights: {e}")

@command("goodtalk", "Start continuous conversation with AI")
async def good_talk(ctx):
    """
    Start a continuous conversation with AI
    Usage: /goodtalk
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first.")
        return
    
    user_id = str(ctx.author.id)
    channel_id = str(ctx.channel.id)
    
    if user_id in continuous_conversations:
        await ctx.send("🗣️ You already have an active conversation! Type 'stop' to end it first.")
        return
    
    # Initialize continuous conversation
    continuous_conversations[user_id] = {
        "channel_id": channel_id,
        "start_time": datetime.now(),
        "message_count": 0
    }
    
    embed = discord.Embed(
        title="🗣️ Good Talk Started!",
        description="I'm ready for a continuous conversation with you!\n\n"
                   "Just type your messages normally - I'll respond to everything.\n"
                   "Type **'stop'** when you want to end our conversation.",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_footer(text="Continuous conversation mode activated")
    
    await ctx.send(embed=embed)
    
    # Start the conversation with context
    initial_prompt = f"""You are now in continuous conversation mode with {ctx.author.name}. 

Key guidelines:
1. Respond naturally and conversationally
2. Remember the conversation context
3. Be engaging, thoughtful, and helpful
4. Ask follow-up questions to keep the conversation flowing
5. Draw on any relevant information from their RAG data when appropriate

Start by greeting them and asking what they'd like to talk about."""
    
    try:
        ai_response = ollama.chat(initial_prompt, user_id, f"goodtalk_{datetime.now().date()}")
        await ctx.send(f"🤖 {ai_response}")
        continuous_conversations[user_id]["message_count"] += 1
    except Exception as e:
        await ctx.send(f"❌ Error starting conversation: {e}")
        del continuous_conversations[user_id]

@command("aicode", "Start collaborative coding session")
async def ai_code(ctx):
    """
    Start a collaborative coding session with AI
    Usage: /aicode
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first.")
        return
    
    user_id = str(ctx.author.id)
    channel_id = str(ctx.channel.id)
    
    if user_id in active_conversations:
        await ctx.send("💻 You already have an active coding session! Type 'exit' to end it first.")
        return
    
    # Initialize coding conversation
    active_conversations[user_id] = {
        "type": "coding",
        "channel_id": channel_id,
        "start_time": datetime.now(),
        "message_count": 0
    }
    
    embed = discord.Embed(
        title="💻 AI Code Collaboration Started!",
        description="Let's build something amazing together!\n\n"
                   "I can help you with:\n"
                   "• Writing code in any language\n"
                   "• Debugging and optimization\n"
                   "• Architecture and design patterns\n"
                   "• Code review and suggestions\n"
                   "• Real-time feedback and iteration\n\n"
                   "Type **'exit'** when you're done coding.",
        color=0x00ff7f,
        timestamp=datetime.now()
    )
    embed.set_footer(text="Collaborative coding mode activated")
    
    await ctx.send(embed=embed)
    
    # Start with coding context
    initial_prompt = f"""You are now in collaborative coding mode with {ctx.author.name}.

Guidelines for coding collaboration:
1. Provide clear, well-commented code
2. Explain your reasoning and approach
3. Ask clarifying questions about requirements
4. Suggest improvements and alternatives
5. Help debug issues step by step
6. Use proper markdown code blocks for code snippets
7. Be patient and educational

Ask them what they want to build or work on!"""
    
    try:
        ai_response = ollama.chat(initial_prompt, user_id, f"aicode_{datetime.now().date()}")
        await ctx.send(f"💻 {ai_response}")
        active_conversations[user_id]["message_count"] += 1
    except Exception as e:
        await ctx.send(f"❌ Error starting coding session: {e}")
        del active_conversations[user_id]

@command("blowmymind", "Get mind-blowing information")
async def blow_my_mind(ctx):
    """
    Get next-level, mind-blowing information
    Usage: /blowmymind
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first.")
        return
    
    await ctx.send("🤯 Preparing to blow your mind...")
    
    try:
        prompt = """Share something absolutely mind-blowing that most people don't know. This should be:

1. Scientifically fascinating or philosophically profound
2. Counter-intuitive or paradigm-shifting
3. Recent discoveries or ancient wisdom
4. Something that changes how we see reality
5. Beyond ordinary imagination

Examples could be from:
- Quantum physics and consciousness
- Cosmic scale and time
- Biological complexity
- Mathematical beauty
- Technological possibilities
- Historical mysteries
- Future predictions

Make it engaging, accurate, and truly mind-expanding!"""
        
        ai_response = ollama.chat(prompt, str(ctx.author.id), "mind_blowing")
        
        embed = discord.Embed(
            title="🤯 Mind = Blown",
            description=ai_response,
            color=0xff00ff,
            timestamp=datetime.now()
        )
        embed.set_footer(text="🌌 The universe is stranger than we can imagine")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error generating mind-blowing content: {e}")

@command("psychology", "Start AI psychology therapy session")
async def psychology_session(ctx):
    """
    Start an AI psychology therapy session
    Usage: /psychology
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama is not running!**\nPlease start Ollama first.")
        return
    
    user_id = str(ctx.author.id)
    channel_id = str(ctx.channel.id)
    
    if user_id in active_conversations:
        await ctx.send("🧠 You already have an active session! Type 'end' to finish it first.")
        return
    
    # Initialize therapy conversation
    active_conversations[user_id] = {
        "type": "therapy",
        "channel_id": channel_id,
        "start_time": datetime.now(),
        "message_count": 0
    }
    
    embed = discord.Embed(
        title="🧠 AI Psychology Session",
        description="Welcome to your personal AI psychology session.\n\n"
                   "**Important:** This is for support and reflection, not professional therapy.\n\n"
                   "I can help with:\n"
                   "• Self-reflection and awareness\n"
                   "• Cognitive patterns and thoughts\n"
                   "• Emotional processing\n"
                   "• Goal setting and motivation\n"
                   "• Stress and anxiety management\n\n"
                   "Type **'end'** when you're ready to finish.\n"
                   "For serious mental health concerns, please consult a professional.",
        color=0x3498db,
        timestamp=datetime.now()
    )
    embed.set_footer(text="AI Psychology Support - Not a replacement for professional help")
    
    await ctx.send(embed=embed)
    
    # Start therapy session
    therapy_prompt = f"""You are now acting as a supportive AI psychology assistant for {ctx.author.name}.

Guidelines:
1. Be empathetic, non-judgmental, and supportive
2. Ask thoughtful, open-ended questions
3. Help them explore their thoughts and feelings
4. Provide gentle insights and coping strategies
5. Encourage self-reflection and growth
6. Always remind them this isn't professional therapy
7. Be warm but maintain appropriate boundaries

Start by asking how they're feeling today and what they'd like to explore."""
    
    try:
        ai_response = ollama.chat(therapy_prompt, user_id, f"psychology_{datetime.now().date()}")
        await ctx.send(f"🧠 {ai_response}")
        active_conversations[user_id]["message_count"] += 1
    except Exception as e:
        await ctx.send(f"❌ Error starting psychology session: {e}")
        del active_conversations[user_id]

# Event listener for continuous conversations
@commands.Cog.listener()
async def on_message(message):
    """Handle continuous conversation messages"""
    if message.author.bot:
        return
    
    user_id = str(message.author.id)
    channel_id = str(message.channel.id)
    
    # Handle stop commands for continuous conversations
    if message.content.lower() in ['stop', 'exit', 'end', 'quit']:
        if user_id in continuous_conversations:
            session = continuous_conversations[user_id]
            duration = datetime.now() - session['start_time']
            
            embed = discord.Embed(
                title="🗣️ Good Talk Ended",
                description=f"Thanks for the great conversation!\n\n"
                           f"**Duration:** {duration}\n"
                           f"**Messages:** {session['message_count']}",
                color=0xff6b6b,
                timestamp=datetime.now()
            )
            await message.channel.send(embed=embed)
            del continuous_conversations[user_id]
            return
        
        if user_id in active_conversations:
            session = active_conversations[user_id]
            duration = datetime.now() - session['start_time']
            session_type = session.get('type', 'conversation')
            
            embed = discord.Embed(
                title=f"{'💻' if session_type == 'coding' else '🧠'} Session Ended",
                description=f"Thanks for the {session_type} session!\n\n"
                           f"**Duration:** {duration}\n"
                           f"**Messages:** {session['message_count']}",
                color=0xff6b6b,
                timestamp=datetime.now()
            )
            await message.channel.send(embed=embed)
            del active_conversations[user_id]
            return
    
    # Handle continuous conversation responses
    if user_id in continuous_conversations:
        session = continuous_conversations[user_id]
        if session['channel_id'] == channel_id:
            if ollama.check_ollama_status():
                try:
                    # Get context from RAG if available
                    search_results = rag_system.search_documents(message.content, limit=2)
                    context = ""
                    if search_results:
                        context = f"\n\nRelevant context: {search_results[0]['content'][:200]}"
                    
                    prompt = f"Continue our conversation. User said: {message.content}{context}"
                    ai_response = ollama.chat(prompt, user_id, f"goodtalk_{datetime.now().date()}")
                    
                    await message.channel.send(f"🤖 {ai_response}")
                    session['message_count'] += 1
                except Exception as e:
                    await message.channel.send(f"❌ Error in conversation: {e}")
    
    # Handle active conversation sessions (coding, therapy)
    elif user_id in active_conversations:
        session = active_conversations[user_id]
        if session['channel_id'] == channel_id:
            if ollama.check_ollama_status():
                try:
                    session_type = session.get('type', 'general')
                    
                    if session_type == 'coding':
                        prompt = f"Continue our coding collaboration. User said: {message.content}"
                        icon = "💻"
                    elif session_type == 'therapy':
                        prompt = f"Continue our psychology session. User said: {message.content}"
                        icon = "🧠"
                    else:
                        prompt = f"Continue our conversation. User said: {message.content}"
                        icon = "🤖"
                    
                    ai_response = ollama.chat(prompt, user_id, f"{session_type}_{datetime.now().date()}")
                    
                    await message.channel.send(f"{icon} {ai_response}")
                    session['message_count'] += 1
                except Exception as e:
                    await message.channel.send(f"❌ Error in {session_type} session: {e}")

# Daily reflection task (runs at 16:00)
@tasks.loop(time=time(16, 0))  # 4:00 PM
async def daily_reflection_reminder():
    """Send daily reflection reminder at 16:00"""
    # This would need to be configured with the specific channel/user
    # For now, it's a placeholder for the scheduled task
    pass

# Initialize the daily task when the module loads
@commands.Cog.listener()
async def on_ready():
    """Start daily tasks when bot is ready"""
    if not daily_reflection_reminder.is_running():
        daily_reflection_reminder.start()

