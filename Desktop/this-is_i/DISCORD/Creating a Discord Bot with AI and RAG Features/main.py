import discord
from discord.ext import commands, tasks
import ollama
import requests
from bs4 import BeautifulSoup
import asyncio
import os
import sys
from pathlib import Path

# --- Configuration ---
import config

# --- Ollama Integration ---
sys.path.append(str(Path(__file__).parent / "ollama_integration"))
from ollama_integration import OllamaIntegration

# --- Daily Scheduler ---
from daily_scheduler import init_scheduler, daily_scheduler_loop

# Initialize Ollama integration
ollama_integration = OllamaIntegration()

# Ensure RAG data folder exists
if not os.path.exists(config.RAG_DATA_FOLDER):
    os.makedirs(config.RAG_DATA_FOLDER)

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True  # Required for accessing message content
bot = commands.Bot(command_prefix='/', intents=intents)

# --- RAG Knowledge Base ---
r_a_g_documents = [] # This will be dynamically updated

def retrieve_context(query, documents):
    # Simple keyword-based retrieval for demonstration
    relevant_docs = [doc for doc in documents if any(keyword in doc.lower() for keyword in query.lower().split())]
    return "\n".join(relevant_docs)

async def get_ollama_response(prompt, context=None):
    """Get response from Ollama using the new integration"""
    try:
        user_id = "discord_bot"
        session_id = "rag_session"
        response = ollama_integration.chat(prompt, user_id, session_id, context)
        return response
    except Exception as e:
        return f"Error communicating with Ollama: {e}. Please ensure Ollama is running and the model '{config.OLLAMA_MODEL}' is pulled."

# --- Web Scraping for RAG ---
async def scrape_url_for_rag(url):
    try:
        print(f"Attempting to scrape {url}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from common elements like paragraphs and list items
        text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'li'])])
        # Store content in a file within the RAG data folder
        filename = os.path.join(config.RAG_DATA_FOLDER, f"rag_content_{len(r_a_g_documents)}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text_content)
        r_a_g_documents.append(f"Content from {url} stored in {filename}") # Store reference to file
        print(f"Scraped {url} and added to RAG documents. Current RAG docs count: {len(r_a_g_documents)}")
        return True
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return False

@tasks.loop(seconds=config.RAG_FETCH_INTERVAL_SECONDS)
async def continuous_rag_fetch():
    print("Starting continuous RAG data fetch...")
    for url in config.RAG_SOURCES:
        await scrape_url_for_rag(url)
    print("Finished continuous RAG data fetch.")

# --- MCP Marketplace Placeholder ---
mcp_servers = {
    "ollama_chat_server": {
        "description": "A server for advanced Ollama chat interactions. Offers various LLMs.",
        "version": "1.0",
        "developer": "AI Innovators",
        "download_link": "https://example.com/ollama_chat_server_v1.zip"
    },
    "ollama_gui_server": {
        "description": "A GUI-based server for managing Ollama models and deployments.",
        "version": "1.2",
        "developer": "Model Masters",
        "download_link": "https://example.com/ollama_gui_server_v1.2.zip"
    },
    "rag_processor_mcp": {
        "description": "An MCP server dedicated to processing and indexing RAG data sources.",
        "version": "0.9 beta",
        "developer": "Data Weavers",
        "download_link": "https://example.com/rag_processor_mcp_beta.zip"
    }
}

# --- Events ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    
    # Initialize scheduler
    scheduler = init_scheduler(bot)
    print("Daily scheduler initialized.")
    
    # Start background tasks
    continuous_rag_fetch.start() # Start the continuous RAG fetching task
    print("Continuous RAG fetch task started.")
    
    # Start daily scheduler loop
    if not daily_scheduler_loop.is_running():
        daily_scheduler_loop.start()
        print("Daily scheduler loop started.")

@bot.event
async def on_message(message):
    """Handle message events for XP system and AI context"""
    if message.author.bot:
        return
    
    # Process XP for user messages
    try:
        from commands.utility_management_commands import add_user_xp
        await add_user_xp(message.author.id, message.guild.id if message.guild else 0, 5)
    except Exception as e:
        print(f"Error processing XP: {e}")
    
    # Process commands
    await bot.process_commands(message)

# --- Command System ---
from command_manager import CommandManager

# Initialize command manager
command_manager = CommandManager(bot)

# Load all commands from the commands directory
command_manager.load_all_commands()

# Register commands from loaded modules
for cmd_name, cmd_func in command_manager.loaded_commands.items():
    # Skip if command already exists
    if cmd_name in [cmd.name for cmd in bot.commands]:
        print(f"⚠️ Skipping duplicate command: {cmd_name}")
        continue
    
    # Create a proper command wrapper that preserves the function signature
    def create_command_wrapper(func):
        @bot.command(name=cmd_name)
        async def command_wrapper(ctx, *args, **kwargs):
            try:
                # Get function signature to determine how many arguments it expects
                import inspect
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                
                # Handle different function signatures
                if len(params) == 1:
                    # Function only takes ctx
                    await func(ctx)
                elif len(params) == 2:
                    param_name = params[1]
                    if param_name.startswith('*'):
                        # Function takes ctx and *args
                        await func(ctx, *args)
                    else:
                        # Function takes ctx and one argument
                        if args:
                            await func(ctx, args[0])
                        else:
                            await func(ctx, "")
                else:
                    # Try to call with all arguments
                    await func(ctx, *args, **kwargs)
            except Exception as e:
                await ctx.send(f"❌ Error executing command: {e}")
        return command_wrapper
    
    create_command_wrapper(cmd_func)

# --- Legacy Commands (for backward compatibility) ---
@bot.command(name='scrape')
async def scrape_command(ctx, url: str):
    await ctx.send(f"Attempting to scrape {url} for RAG data...")
    success = await scrape_url_for_rag(url)
    if success:
        await ctx.send(f"Successfully scraped {url} and updated RAG knowledge base.")
    else:
        await ctx.send(f"Failed to scrape {url}. Check the URL or bot console for errors.")

@bot.command(name='listmcp')
async def list_mcp(ctx):
    if not mcp_servers:
        await ctx.send("No MCP servers available at the moment.")
        return
    
    response_message = "Available MCP Servers:\n"
    for name, details in mcp_servers.items():
        response_message += f"**{name}** (v{details['version']}) by {details['developer']}: {details['description']}\n"
    await ctx.send(response_message)

@bot.command(name='downloadmcp')
async def download_mcp(ctx, server_name):
    server_name = server_name.lower()
    if server_name in mcp_servers:
        details = mcp_servers[server_name]
        await ctx.send(f"Downloading {server_name}: {details['download_link']}")
        await ctx.send(f"(In a real scenario, this would initiate a download or deployment of {server_name})")
    else:
        await ctx.send(f"MCP server '{server_name}' not found. Use `/listmcp` to see available servers.")

@bot.command(name='addmcp')
async def add_mcp(ctx, name: str, description: str, version: str, developer: str, download_link: str):
    if name.lower() in mcp_servers:
        await ctx.send(f"MCP server '{name}' already exists. Use a different name or update the existing entry.")
        return
    mcp_servers[name.lower()] = {
        "description": description,
        "version": version,
        "developer": developer,
        "download_link": download_link
    }
    await ctx.send(f"MCP server '{name}' added to the marketplace.")

@bot.command(name='createcmd')
async def create_command(ctx, command_name: str, description: str = ""):
    """Create a new command interactively"""
    try:
        file_path = command_manager.create_command_template(command_name, description)
        await ctx.send(f"✅ Created command template: `/createcmd`\n📁 File: {file_path}\n🔄 Restart bot to load the new command!")
    except Exception as e:
        await ctx.send(f"❌ Error creating command: {e}")

# --- Run Bot ---
if __name__ == '__main__':
    bot.run(config.DISCORD_BOT_TOKEN)

