#!/usr/bin/env python3
"""
Danish Advanced Commands Module
Advanced Danish features including quest generation, debate moderation, and specialized tools
"""

import discord
from discord.ext import commands
from command_manager import command
import asyncio
import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime
import subprocess
import tempfile
import base64

# Add ollama integration to path
sys.path.append(str(Path(__file__).parent.parent / "ollama_integration"))
from ollama_integration import OllamaIntegration

# Add RAG system to path
sys.path.append(str(Path(__file__).parent.parent))
from rag_system import RAGSystem

# Initialize systems
ollama = OllamaIntegration()
rag_system = RAGSystem()

# Quest and game data storage
GAME_DATA_DIR = Path(__file__).parent.parent / "game_data"
GAME_DATA_DIR.mkdir(exist_ok=True)

# Active quests and debates
active_quests = {}
active_debates = {}
user_economy = {}

@command("dynamiskquest", "Generer dynamisk quest baseret på serverhistorik")
async def dynamic_quest(ctx, *, tema: str = None):
    """
    Generer en dynamisk quest baseret på brugerinteraktioner og serverhistorik
    Usage: /dynamiskquest [tema]
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    await ctx.send("🎯 Genererer dynamisk quest...")
    
    try:
        # Søg i RAG system for server kontekst
        search_query = tema if tema else f"server {ctx.guild.name} aktivitet"
        search_results = rag_system.search_documents(search_query, limit=5)
        
        server_context = ""
        if search_results:
            server_context = "\n".join([result['content'][:200] for result in search_results])
        
        prompt = f"""Generer en spændende, kontekstafhængig quest til et Discord RPG baseret på:

Server: {ctx.guild.name}
Tema: {tema if tema else "Generel adventure"}
Server kontekst: {server_context}

Opret en quest der:
1. Passer til serveren og dens medlemmer
2. Har klare mål og belønninger
3. Inkluderer interessante udfordringer
4. Kan gennemføres via Discord kommandoer
5. Har en god historie/baggrund

Format som en rigtig RPG quest med:
- Titel
- Baggrund/historie
- Mål og opgaver
- Belønninger
- Tidsramme
- Næste skridt

Skriv på dansk og gør det engagerende!"""
        
        ai_response = ollama.chat(prompt, str(ctx.author.id), "quest_generation")
        
        # Store quest data
        quest_id = f"quest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        quest_data = {
            "id": quest_id,
            "creator": ctx.author.name,
            "guild": ctx.guild.name,
            "tema": tema,
            "content": ai_response,
            "created": datetime.now().isoformat(),
            "participants": [],
            "status": "active"
        }
        
        quest_file = GAME_DATA_DIR / f"{quest_id}.json"
        with open(quest_file, 'w', encoding='utf-8') as f:
            json.dump(quest_data, f, ensure_ascii=False, indent=2)
        
        active_quests[quest_id] = quest_data
        
        embed = discord.Embed(
            title="🎯 Dynamisk Quest Genereret!",
            description=ai_response,
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.add_field(name="Quest ID", value=quest_id, inline=True)
        embed.add_field(name="Status", value="🟢 Aktiv", inline=True)
        embed.set_footer(text="Brug /joinquest for at deltage!")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Fejl ved quest generering: {e}")

@command("hvadvis", "Simuler hypotetiske scenarier")
async def what_if_game(ctx, *, scenarie: str):
    """
    Hvad hvis spil - simuler hypotetiske scenarier
    Usage: /hvadvis <scenarie>
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    await ctx.send("🤔 Simulerer scenarie...")
    
    try:
        prompt = f"""Du er en ekspert historiker og futurist. Simuler dette hypotetiske scenarie: "{scenarie}"

Analyser:
1. Umiddelbare konsekvenser
2. Langsigtede effekter
3. Sandsynlige udviklinger
4. Alternative udfald
5. Historiske paralleller

Giv et detaljeret, realistisk svar på dansk der:
- Er baseret på historisk viden
- Overvejer komplekse årsag-virkning forhold
- Inkluderer både positive og negative konsekvenser
- Er engagerende og tankevækkende

Vær kreativ men realistisk!"""
        
        ai_response = ollama.chat(prompt, str(ctx.author.id), "what_if_simulation")
        
        embed = discord.Embed(
            title="🤔 Hvad Hvis Simulation",
            description=f"**Scenarie:** {scenarie}\n\n{ai_response}",
            color=0x3498db,
            timestamp=datetime.now()
        )
        embed.set_footer(text="🔮 Hypotetisk simulation baseret på AI analyse")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Fejl ved simulation: {e}")

@command("debatmoderator", "Start AI-modereret debat")
async def debate_moderator(ctx, *, emne: str):
    """
    Start en AI-modereret debat om et emne
    Usage: /debatmoderator <emne>
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    debate_id = f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize debate
    active_debates[debate_id] = {
        "topic": emne,
        "moderator": ctx.author.id,
        "participants": [],
        "arguments": [],
        "start_time": datetime.now(),
        "status": "open"
    }
    
    embed = discord.Embed(
        title="🗣️ AI Debat Moderator",
        description=f"**Debat Emne:** {emne}\n\n"
                   f"Jeg vil moderere denne debat og sikre fair diskussion.\n\n"
                   f"**Regler:**\n"
                   f"• Respektfuld tone\n"
                   f"• Faktabaserede argumenter\n"
                   f"• Lyt til andre synspunkter\n"
                   f"• Jeg opsummerer løbende\n\n"
                   f"**Kommandoer:**\n"
                   f"`/argument <dit argument>` - Tilføj argument\n"
                   f"`/debatsammendrag` - Få sammendrag\n"
                   f"`/slutdebat` - Afslut debat",
        color=0xe74c3c,
        timestamp=datetime.now()
    )
    embed.add_field(name="Debat ID", value=debate_id, inline=True)
    embed.add_field(name="Status", value="🟢 Åben", inline=True)
    embed.set_footer(text="AI Debat Moderator - Fair og balanceret diskussion")
    
    await ctx.send(embed=embed)
    
    # AI moderator introduction
    try:
        intro_prompt = f"""Du er nu debat moderator for emnet: "{emne}"

Som AI moderator skal du:
1. Præsentere emnet neutralt
2. Opfordre til konstruktiv diskussion
3. Stille relevante spørgsmål
4. Sikre alle synspunkter høres

Start debatten med en neutral introduktion på dansk."""
        
        ai_intro = ollama.chat(intro_prompt, "debate_moderator", debate_id)
        await ctx.send(f"🤖 **AI Moderator:** {ai_intro}")
        
    except Exception as e:
        await ctx.send(f"❌ Fejl ved debat start: {e}")

@command("osintai", "Start kollaborativt OSINT arbejde")
async def osint_ai(ctx, *, target: str = None):
    """
    Start kollaborativt OSINT (Open Source Intelligence) arbejde
    Usage: /osintai [target]
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    # Security warning
    embed = discord.Embed(
        title="🔍 OSINT AI Kollaboration",
        description="**⚠️ VIGTIG SIKKERHEDSADVARSEL ⚠️**\n\n"
                   "OSINT skal kun bruges til:\n"
                   "• Lovlige formål\n"
                   "• Offentligt tilgængelig information\n"
                   "• Uddannelsesmæssige øjemed\n"
                   "• Autoriserede penetrationstest\n\n"
                   "**ALDRIG til:**\n"
                   "• Ulovlig overvågning\n"
                   "• Krænkelse af privatliv\n"
                   "• Stalking eller chikane\n"
                   "• Uautoriserede aktiviteter",
        color=0xff9900,
        timestamp=datetime.now()
    )
    
    if target:
        embed.add_field(
            name="🎯 Target",
            value=f"`{target}`",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ OSINT Værktøjer",
            value="• Shodan søgninger\n"
                  "• DNS enumeration\n"
                  "• Social media analyse\n"
                  "• Metadata extraction\n"
                  "• Passive reconnaissance",
            inline=True
        )
        
        embed.add_field(
            name="📋 Næste Skridt",
            value="• Bekræft autorisation\n"
                  "• Definer scope\n"
                  "• Vælg metoder\n"
                  "• Start indsamling\n"
                  "• Analyser resultater",
            inline=True
        )
    
    embed.set_footer(text="🔒 Husk altid at følge lovgivning og etiske retningslinjer")
    
    await ctx.send(embed=embed)
    
    if target and ollama.check_ollama_status():
        try:
            osint_prompt = f"""Som OSINT ekspert, hjælp med at planlægge lovlig reconnaissance af: {target}

Foreslå:
1. Passive informationsindsamling metoder
2. Offentlige databaser at søge i
3. OSINT værktøjer der kan bruges
4. Struktureret tilgang til analyse
5. Dokumentation og rapportering

Fokuser på lovlige, etiske metoder og offentligt tilgængelig information.
Advarer mod ulovlige aktiviteter.

Svar på dansk."""
            
            ai_response = ollama.chat(osint_prompt, str(ctx.author.id), "osint_collaboration")
            
            osint_embed = discord.Embed(
                title="🔍 OSINT Analyse Plan",
                description=ai_response,
                color=0x00ff7f,
                timestamp=datetime.now()
            )
            osint_embed.set_footer(text="⚖️ Kun til lovlige og etiske formål")
            
            await ctx.send(embed=osint_embed)
            
        except Exception as e:
            await ctx.send(f"❌ Fejl ved OSINT analyse: {e}")

@command("redteam1", "Prompt Chaining Engine for Red Team")
async def red_team_prompt_chain(ctx, *, scenario: str):
    """
    Automated red team prompt chaining for authorized testing
    Usage: /redteam1 <scenario>
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    # Authorization check embed
    auth_embed = discord.Embed(
        title="🔴 RED TEAM AUTORISATION PÅKRÆVET",
        description="**⚠️ KRITISK SIKKERHEDSADVARSEL ⚠️**\n\n"
                   "Red Team aktiviteter må KUN udføres med:\n"
                   "• Skriftlig autorisation\n"
                   "• Klart defineret scope\n"
                   "• Juridisk godkendelse\n"
                   "• Professionel kontrakt\n\n"
                   "**Bekræft at du har autorisation til:**\n"
                   f"• Scenario: `{scenario}`\n"
                   "• Penetrationstest\n"
                   "• Payload udvikling\n"
                   "• Sikkerhedstest",
        color=0xff0000,
        timestamp=datetime.now()
    )
    auth_embed.set_footer(text="🚨 Uautoriserede aktiviteter er ulovlige")
    
    await ctx.send(embed=auth_embed)
    
    # Wait for confirmation
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['ja', 'yes', 'bekræft', 'confirm']
    
    try:
        await ctx.send("**Skriv 'ja' eller 'bekræft' for at fortsætte med autoriseret red team test:**")
        msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
        
        if msg:
            await ctx.send("🔴 **AUTORISERET RED TEAM TEST STARTET**")
            
            # Prompt chaining for red team
            chain_prompt = f"""Som autoriseret red team ekspert, analyser dette scenario: {scenario}

Udfør automatisk prompt chaining:

1. **ANALYSE FASE:**
   - Identificer potentielle sårbarheder
   - Vurder angrebsoverflader
   - Prioriter targets

2. **PAYLOAD UDVIKLING:**
   - Foreslå relevante payloads
   - Tilpas til target miljø
   - Overvej evasion teknikker

3. **DELIVERY METODER:**
   - Evaluér leveringsmekanismer
   - Social engineering vinkler
   - Tekniske leveringsmetoder

4. **MITIGERING:**
   - Foreslå forsvar
   - Detektionsmetoder
   - Remediering

Alt skal være til AUTORISERET penetrationstest. Svar på dansk."""
            
            ai_response = ollama.chat(chain_prompt, str(ctx.author.id), "redteam_authorized")
            
            redteam_embed = discord.Embed(
                title="🔴 Red Team Analyse (AUTORISERET)",
                description=ai_response,
                color=0xff4444,
                timestamp=datetime.now()
            )
            redteam_embed.set_footer(text="🔒 Kun til autoriseret penetrationstest")
            
            await ctx.send(embed=redteam_embed)
            
    except asyncio.TimeoutError:
        await ctx.send("⏰ **Timeout** - Red team session afbrudt. Ingen autorisation bekræftet.")
    except Exception as e:
        await ctx.send(f"❌ Fejl ved red team analyse: {e}")

@command("gophish", "AI-genererede social engineering scenarier")
async def gophish_scenarios(ctx, *, target_type: str = "generel"):
    """
    Generer AI-baserede social engineering awareness scenarier
    Usage: /gophish [target_type]
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    # Educational disclaimer
    disclaimer_embed = discord.Embed(
        title="🎣 Social Engineering Awareness",
        description="**📚 UDDANNELSESFORMÅL**\n\n"
                   "Dette værktøj genererer social engineering scenarier til:\n"
                   "• Sikkerhedstræning\n"
                   "• Awareness kampagner\n"
                   "• Phishing simulation (autoriseret)\n"
                   "• Uddannelsesmæssige øjemed\n\n"
                   "**⚠️ MÅ IKKE bruges til:**\n"
                   "• Ægte phishing angreb\n"
                   "• Ulovlige aktiviteter\n"
                   "• Manipulation af personer\n"
                   "• Uautoriserede test",
        color=0xffa500,
        timestamp=datetime.now()
    )
    
    await ctx.send(embed=disclaimer_embed)
    
    try:
        phish_prompt = f"""Generer et realistisk social engineering awareness scenarie for: {target_type}

Opret et uddannelsesscenarie der:
1. Viser almindelige phishing teknikker
2. Forklarer hvordan man identificerer trusler
3. Giver konkrete eksempler
4. Inkluderer forebyggende tiltag
5. Er realistisk men ikke skadeligt

Fokuser på:
- Email phishing
- Spear phishing
- Pretexting
- Baiting
- Quid pro quo

Formatet som en træningscase med:
- Scenarie beskrivelse
- Red flags at kigge efter
- Korrekt respons
- Læringsmål

Svar på dansk og gør det uddannelsesmæssigt værdifuldt."""
        
        ai_response = ollama.chat(phish_prompt, str(ctx.author.id), "phishing_awareness")
        
        awareness_embed = discord.Embed(
            title="🎣 Social Engineering Awareness Scenarie",
            description=ai_response,
            color=0x00ff7f,
            timestamp=datetime.now()
        )
        awareness_embed.set_footer(text="📚 Kun til uddannelse og awareness")
        
        await ctx.send(embed=awareness_embed)
        
    except Exception as e:
        await ctx.send(f"❌ Fejl ved scenarie generering: {e}")

@command("integratepromt", "Integrer permanent prompt i RAG system")
async def integrate_prompt(ctx, *, prompt: str):
    """
    Integrer en permanent prompt som Ollama altid læser
    Usage: /integratepromt <prompt>
    """
    try:
        # Create integrated prompt file
        integrated_prompts_file = Path(__file__).parent.parent / "rag_documents" / "integrated_prompts.txt"
        
        # Read existing prompts
        existing_prompts = ""
        if integrated_prompts_file.exists():
            with open(integrated_prompts_file, 'r', encoding='utf-8') as f:
                existing_prompts = f.read()
        
        # Add new prompt with timestamp
        new_entry = f"\n\n--- Integrated Prompt ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n"
        new_entry += f"Added by: {ctx.author.name}\n"
        new_entry += f"Prompt: {prompt}\n"
        new_entry += "--- End Prompt ---"
        
        # Write updated prompts
        with open(integrated_prompts_file, 'w', encoding='utf-8') as f:
            f.write(existing_prompts + new_entry)
        
        # Add to RAG system
        rag_system.add_document(integrated_prompts_file)
        
        embed = discord.Embed(
            title="✅ Prompt Integreret",
            description=f"Din prompt er nu permanent integreret i RAG systemet:\n\n"
                       f"**Prompt:** {prompt}\n\n"
                       f"Ollama vil nu altid have adgang til denne prompt i alle svar.",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.set_footer(text="🧠 Prompt er nu del af AI's permanente hukommelse")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Fejl ved prompt integration: {e}")

@command("payloadstego", "Steganografi payload profil")
async def payload_stego_profile(ctx):
    """
    Generer steganografi payload profil til autoriseret test
    Usage: /payloadstego
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    # Authorization warning
    auth_embed = discord.Embed(
        title="🔒 STEGANOGRAFI AUTORISATION",
        description="**⚠️ SIKKERHEDSADVARSEL ⚠️**\n\n"
                   "Steganografi værktøjer må kun bruges til:\n"
                   "• Autoriseret penetrationstest\n"
                   "• Sikkerhedsforskning\n"
                   "• Uddannelsesmæssige formål\n"
                   "• Lovlige security assessments\n\n"
                   "**ALDRIG til ulovlige aktiviteter!**",
        color=0xff9900,
        timestamp=datetime.now()
    )
    
    await ctx.send(embed=auth_embed)
    
    try:
        stego_prompt = """Som cybersecurity ekspert, beskriv steganografi teknikker til autoriseret penetrationstest:

1. **IMAGE STEGANOGRAFI:**
   - LSB (Least Significant Bit) metoder
   - Metadata embedding
   - Palette-baseret skjulning

2. **PAYLOAD DELIVERY:**
   - Executable embedding
   - Script injection
   - Data exfiltration

3. **DETECTION EVASION:**
   - Anti-forensic teknikker
   - Noise addition
   - Compression resistance

4. **VÆRKTØJER:**
   - Steghide
   - OpenStego
   - Custom scripts

5. **FORSVAR:**
   - Steganalysis metoder
   - Detection værktøjer
   - Preventive tiltag

Fokuser på autoriseret brug og forsvar. Svar på dansk."""
        
        ai_response = ollama.chat(stego_prompt, str(ctx.author.id), "steganography_profile")
        
        stego_embed = discord.Embed(
            title="🔒 Steganografi Profil (AUTORISERET)",
            description=ai_response,
            color=0x9b59b6,
            timestamp=datetime.now()
        )
        stego_embed.set_footer(text="🛡️ Kun til autoriseret sikkerhedstest")
        
        await ctx.send(embed=stego_embed)
        
    except Exception as e:
        await ctx.send(f"❌ Fejl ved steganografi profil: {e}")

@command("learningpath", "Personaliseret læringsforløb")
async def personalized_learning_path(ctx, *, emne: str):
    """
    Design skræddersyet læringsforløb baseret på brugerdata
    Usage: /learningpath <emne>
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    await ctx.send("📚 Designer personaliseret læringsforløb...")
    
    try:
        # Get user context from RAG
        search_results = rag_system.search_documents(f"user {ctx.author.name} interesse", limit=5)
        user_context = ""
        if search_results:
            user_context = "\n".join([result['content'][:200] for result in search_results])
        
        learning_prompt = f"""Design et personaliseret læringsforløb for: {emne}

Bruger kontekst:
{user_context}

Opret et struktureret læringsforløb der:
1. Starter med brugerens nuværende niveau
2. Bygger gradvist på viden
3. Inkluderer praktiske øvelser
4. Har klare milepæle
5. Tilpasser sig brugerens interesser

Strukturer som:
- Forudsætninger
- Læringsmål
- Moduler (1-10)
- Ressourcer for hvert modul
- Praktiske projekter
- Evaluering/tests
- Tidsramme
- Næste skridt

Gør det engagerende og opnåeligt. Svar på dansk."""
        
        ai_response = ollama.chat(learning_prompt, str(ctx.author.id), "learning_path")
        
        # Save learning path
        learning_file = Path(__file__).parent.parent / "rag_documents" / f"learning_path_{ctx.author.name}_{emne.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(learning_file, 'w', encoding='utf-8') as f:
            f.write(f"Personaliseret Læringsforløb: {emne}\n")
            f.write(f"Bruger: {ctx.author.name}\n")
            f.write(f"Oprettet: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(ai_response)
        
        # Add to RAG system
        rag_system.add_document(learning_file)
        
        embed = discord.Embed(
            title="📚 Personaliseret Læringsforløb",
            description=ai_response,
            color=0x3498db,
            timestamp=datetime.now()
        )
        embed.add_field(name="Emne", value=emne, inline=True)
        embed.add_field(name="Tilpasset til", value=ctx.author.name, inline=True)
        embed.set_footer(text="📖 Læringsforløb gemt til din profil")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Fejl ved læringsforløb design: {e}")

@command("chainofthought", "Vis AI's tankeproces")
async def chain_of_thought(ctx, *, spørgsmål: str):
    """
    Vis AI's tankeproces og ræsonnement trin for trin
    Usage: /chainofthought <spørgsmål>
    """
    if not ollama.check_ollama_status():
        await ctx.send("❌ **Ollama kører ikke!** Start Ollama først.")
        return
    
    await ctx.send("🧠 Analyserer tankeproces...")
    
    try:
        cot_prompt = f"""Besvar følgende spørgsmål og vis din komplette tankeproces: {spørgsmål}

Strukturer dit svar som:

**TRIN 1: PROBLEMANALYSE**
- Hvad spørger brugeren om?
- Hvilke nøgleord er vigtige?
- Hvilken type svar er nødvendigt?

**TRIN 2: VIDENSØGNING**
- Hvilken viden er relevant?
- Hvilke kilder kan bruges?
- Hvad ved jeg om emnet?

**TRIN 3: RÆSONNEMENT**
- Hvordan forbinder jeg informationen?
- Hvilke logiske skridt følger jeg?
- Hvilke antagelser gør jeg?

**TRIN 4: SYNTESE**
- Hvordan strukturerer jeg svaret?
- Hvilke eksempler kan hjælpe?
- Hvad er det vigtigste at kommunikere?

**TRIN 5: KVALITETSKONTROL**
- Er svaret komplet?
- Er det forståeligt?
- Mangler der noget?

**ENDELIGT SVAR:**
[Dit komplette svar her]

Vær transparent om din tankeproces. Svar på dansk."""
        
        ai_response = ollama.chat(cot_prompt, str(ctx.author.id), "chain_of_thought")
        
        embed = discord.Embed(
            title="🧠 Chain of Thought Analyse",
            description=ai_response,
            color=0xe74c3c,
            timestamp=datetime.now()
        )
        embed.add_field(name="Spørgsmål", value=spørgsmål, inline=False)
        embed.set_footer(text="🔍 Transparent AI ræsonnement")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Fejl ved tankeproces analyse: {e}")

# Helper function for authorized activities
def check_authorization(user_id: str, activity: str) -> bool:
    """Check if user is authorized for specific activities"""
    # This would integrate with your authorization system
    # For now, return True for demonstration
    return True

# Helper function to log security activities
def log_security_activity(user_id: str, activity: str, details: str):
    """Log security-related activities"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "activity": activity,
        "details": details
    }
    
    log_file = Path(__file__).parent.parent / "security_logs.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')

