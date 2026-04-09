import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render uses the 'PORT' variable automatically
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime

# Load token
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
@bot.hybrid_command(name="startsession", description="Start a session")
@commands.has_permissions(manage_messages=True)
async def startsession(ctx):
    start_embed = discord.Embed(
        title="Session result:",
        description=(
            f"📄 **Reason:** Session Started\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"📍 **Location:** Staff Training Room\n\n"
            f"**Details:**\n"
            f"✔️ The session has officially begun. [@everyone]"
        ),
        color=0x2b2d31
    )
    start_embed.set_footer(text="DGVRP")
    await ctx.send(content="@everyone", embed=start_embed)


@bot.hybrid_command(name="endsession", description="End a session")
@commands.has_permissions(manage_messages=True)
async def endsession(ctx):
    end_embed = discord.Embed(
        title="Session result:",
        description=(
            f"📄 **Reason:** Session Ended\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"🚥 **Status:** Now Closed\n\n"
            f"**Details:**\n"
            f"✔️ The session has concluded."
        ),
        color=0x2b2d31
    )
    end_embed.set_footer(text="DGVRP")
    
    # Removed the content="@everyone" part here
    await ctx.send(embed=end_embed)

# --- INFRACTION SYSTEM ---
@bot.hybrid_command(name="infract", description="Log a custom infraction")
@commands.has_permissions(moderate_members=True)
async def infract(ctx, member: discord.Member, type: str, points: int, *, reason: str = "No reason provided"):
    # Keeps your database logic working
    data = load_data()
    entry = {
        "user": str(member.id),
        "type": type,
        "points": points,
        "reason": reason,
        "admin": str(ctx.author.id),
        "date": str(datetime.now())
    }
    data["infractions"].append(entry)
    save_data(data)

    # Embed matches the Promotion style exactly
    infract_embed = discord.Embed(
        title="Infraction result:",
        description=(
            f"📄 **Reason:** {reason}\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"⚠️ **Type:** {type} ({points} pts)\n\n"
            f"**Infracted:**\n"
            f"✔️ {member.display_name} [{member.id}]"
        ),
        color=0x2b2d31
    )
    infract_embed.set_footer(text="DGVRP")
    await ctx.send(embed=infract_embed)


# --- MODERATION COMMANDS ---
@bot.hybrid_command(name="warn", description="Warn a user")
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    warn_embed = discord.Embed(
        title="Warn result:",
        description=(
            f"📄 **Reason:** {reason}\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"⚠️ **Action:** Warning issued\n\n"
            f"**Warned:**\n"
            f"✔️ {member.display_name} [{member.id}]"
        ),
        color=0x2b2d31
    )
    warn_embed.set_footer(text="DGVRP")
    await ctx.send(embed=warn_embed)

@bot.hybrid_command(name="mute", description="Mute a user")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
    mute_embed = discord.Embed(
        title="Mute result:",
        description=(
            f"📄 **Reason:** {reason}\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"⏳ **Duration:** {duration}\n\n"
            f"**Muted:**\n"
            f"✔️ {member.display_name} [{member.id}]"
        ),
        color=0x2b2d31
    )
    mute_embed.set_footer(text="DGVRP")
    await ctx.send(embed=mute_embed)
    
    # 1. Prepare the Embed first
    
@bot.hybrid_command(name="unmute", description="Unmute a user")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    unmute_embed = discord.Embed(
        title="Unmute result:",
        description=(
            f"📄 **Reason:** {reason}\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"🔊 **Action:** Mute Lifted\n\n"
            f"**Unmuted:**\n"
            f"✔️ {member.display_name} [{member.id}]"
        ),
        color=0x2b2d31
    )
    unmute_embed.set_footer(text="DGVRP")
    await ctx.send(embed=unmute_embed)


@bot.hybrid_command(name="kick", description="Kick a user")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    kick_embed = discord.Embed(
        title="Kick result:",
        description=(
            f"📄 **Reason:** {reason}\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"👢 **Action:** Removed from server\n\n"
            f"**Kicked:**\n"
            f"✔️ {member.display_name} [{member.id}]"
        ),
        color=0x2b2d31
    )
    kick_embed.set_footer(text="DGVRP")
    await ctx.send(embed=kick_embed)

    
@bot.hybrid_command(name="ban", description="Ban a user")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    ban_embed = discord.Embed(
        title="Ban result:",
        description=(
            f"📄 **Reason:** {reason}\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"🚫 **Action:** Permanent Ban\n\n"
            f"**Banned:**\n"
            f"✔️ {member.display_name} [{member.id}]"
        ),
        color=0x2b2d31
    )
    ban_embed.set_footer(text="DGVRP")
    await ctx.send(embed=ban_embed)


# --- PROMOTION ---
@bot.hybrid_command(name="promote", description="Promote a user")
@commands.has_permissions(manage_roles=True)
async def promote(ctx, member: discord.Member, new_rank: discord.Role, *, reason: str = "No reason provided"):
    # The 'reason' is now defined in the line above!
    
    promote_embed = discord.Embed(
        title="Promotion result:",
        description=(
            f"📑 **Reason:** {reason}\n"
            f"👤 **Moderator:** {ctx.author.mention}\n"
            f"⬆️ **New Rank:** {new_rank.mention}\n\n"
            f"**Promoted:**\n"
            f"✅ {member.display_name} [{member.id}]"
        ),
        color=0x2b2d31
    )
    promote_embed.set_footer(text="DGVRP")
    await ctx.send(embed=promote_embed)


bot.run(os.environ.get('TOKEN'))
