import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render uses the 'PORT' variable automatically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
import discord
from discord.ext import commands
from discord import app_commands
import json
from dotenv import load_dotenv
from datetime import datetime

# Load token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Local Data Management
def load_data():
    if not os.path.exists('data.json'):
        return {"infractions": [], "sessions": {}}
    with open('data.json', 'r') as f:
        return json.load(f)

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user} and Slash Commands synced!')

# --- HELPER: Create Embed ---
def create_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
    embed.set_footer(text=f"Admin System")
    return embed

# --- SESSION COMMANDS ---
@bot.hybrid_command(name="startsession", description="Start a staff session")
@commands.has_permissions(manage_messages=True)
async def startsession(ctx):
    embed = create_embed("🚀 Session Started", f"Session started by {ctx.author.mention}", discord.Color.green())
    await ctx.send(embed=embed)

@bot.hybrid_command(name="endsession", description="End a staff session")
@commands.has_permissions(manage_messages=True)
async def endsession(ctx):
    embed = create_embed("🏁 Session Ended", f"Session ended by {ctx.author.mention}", discord.Color.red())
    await ctx.send(embed=embed)

# --- INFRACTION SYSTEM ---
@bot.hybrid_command(name="infract", description="Log a custom infraction")
@commands.has_permissions(moderate_members=True)
async def infract(ctx, member: discord.Member, type: str, *, reason: str):
    data = load_data()
    entry = {
        "user": str(member.id),
        "type": type,
        "reason": reason,
        "admin": str(ctx.author.id),
        "date": str(datetime.now())
    }
    data["infractions"].append(entry)
    save_data(data)
    
    embed = create_embed("⚠️ Infraction Logged", f"**Member:** {member.mention}\n**Type:** {type}\n**Reason:** {reason}", discord.Color.orange())
    await ctx.send(embed=embed)

# --- MODERATION COMMANDS ---
@bot.hybrid_command(name="warn", description="Warn a member")
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason: str):
    embed = create_embed("📝 Warning", f"**Member:** {member.mention}\n**Reason:** {reason}", discord.Color.yellow())
    await ctx.send(embed=embed)

@bot.hybrid_command(name="mute", description="Mute a member (Timeout)")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
    # 1. Prepare the Embed first
    embed = discord.Embed(
        title="🔇 Member Muted",
        description=f"**User:** {member.mention}\n**Duration:** {minutes} minutes\n**Reason:** {reason}",
        color=discord.Color.dark_grey(),
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Action by {ctx.author.name}")

    try:
        # 2. Apply the actual mute
        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        
        # 3. Send the message ONLY if the mute worked
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("❌ **I can't mute this user!** My role must be higher than theirs.")
    except Exception as e:
        await ctx.send(f"⚠️ **Error:** {e}")

@bot.hybrid_command(name="unmute", description="Unmute a member")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    embed = discord.Embed(
        title="🔊 Member Unmuted",
        description=f"{member.mention} has been unmuted.",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )

    try:
        await member.timeout(None)
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ **Forbidden:** I don't have permission to unmute this user.")

@bot.hybrid_command(name="kick", description="Kick a member")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    embed = create_embed("👢 Member Kicked", f"**Member:** {member.mention}\n**Reason:** {reason}")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="ban", description="Ban a member")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    embed = create_embed("🔨 Member Banned", f"**Member:** {member.mention}\n**Reason:** {reason}", discord.Color.dark_red())
    await ctx.send(embed=embed)

# --- PROMOTION ---
@bot.hybrid_command(name="promote", description="Promote a member")
@commands.has_permissions(administrator=True)
async def promote(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    embed = create_embed("📈 Promotion", f"{member.mention} has been promoted to **{role.name}**!", discord.Color.gold())
    await ctx.send(embed=embed)

keep_alive()
bot.run('MTQ5MTI0NTA3NzIzMjg3NzYwOA.Gcejd8.g8YaQrLWMJ7TOLsgN7M9ACXb0l7KaAYbhU723M')
