"""
Discord Voice-Sitter Bot
-------------------------
The only job of this bot is to join a specific voice channel and stay there.
If it gets disconnected for any reason, it automatically tries to rejoin.

Setup:
1. pip install -r requirements.txt
2. Also install ffmpeg on your system (needed by discord.py's voice client
   even though we're not playing audio):
     - Windows: https://ffmpeg.org/download.html (add to PATH)
     - macOS:   brew install ffmpeg
     - Linux:   sudo apt install ffmpeg
3. Copy .env.example to .env and fill in your bot token + channel ID.
4. Run: python bot.py
"""

import asyncio
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
VOICE_CHANNEL_ID = os.getenv("VOICE_CHANNEL_ID")

if not TOKEN:
    raise RuntimeError("Set DISCORD_TOKEN in your .env file")
if not VOICE_CHANNEL_ID:
    raise RuntimeError("Set VOICE_CHANNEL_ID in your .env file")

VOICE_CHANNEL_ID = int(VOICE_CHANNEL_ID)

intents = discord.Intents.default()
intents.voice_states = True  # needed to track voice connection state

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await ensure_connected()
    watchdog.start()


async def ensure_connected():
    """Join the target voice channel if not already connected to it."""
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel is None:
        # Not cached yet, try fetching directly
        try:
            channel = await bot.fetch_channel(VOICE_CHANNEL_ID)
        except discord.HTTPException as e:
            print(f"Could not find voice channel {VOICE_CHANNEL_ID}: {e}")
            return

    if not isinstance(channel, discord.VoiceChannel):
        print(f"Channel {VOICE_CHANNEL_ID} is not a voice channel.")
        return

    guild = channel.guild
    voice_client = guild.voice_client

    if voice_client and voice_client.is_connected():
        if voice_client.channel.id != channel.id:
            print(f"Moving to {channel.name}...")
            await voice_client.move_to(channel)
        return

    print(f"Joining {channel.name} in {guild.name}...")
    try:
        await channel.connect(reconnect=True, self_deaf=True)
    except discord.ClientException as e:
        print(f"Already connecting/connected: {e}")
    except Exception as e:
        print(f"Failed to connect: {e}")


@bot.event
async def on_voice_state_update(member, before, after):
    # Only care about our own bot getting disconnected/moved unexpectedly
    if member.id != bot.user.id:
        return
    if after.channel is None:
        # We got disconnected (kicked, channel deleted, etc.)
        print("Disconnected from voice, attempting to rejoin...")
        await asyncio.sleep(3)
        await ensure_connected()


@tasks.loop(seconds=30)
async def watchdog():
    """Periodic safety check in case events get missed."""
    await ensure_connected()


bot.run(TOKEN)
