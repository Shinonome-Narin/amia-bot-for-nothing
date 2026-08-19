# Discord Voice-Sitter Bot

A minimal bot with one job: join a voice channel and stay there. If it gets
disconnected (kicked, channel deleted, network hiccup, etc.) it automatically
tries to rejoin.

## Setup

1. **Create a bot application**
   - Go to https://discord.com/developers/applications → New Application
   - Go to "Bot" tab → Add Bot → copy the token
   - Under "Privileged Gateway Intents", you don't need to enable any
     (Voice State intent is a normal, non-privileged intent)

2. **Invite the bot to your server**
   - Go to "OAuth2" → "URL Generator"
   - Scopes: `bot`
   - Bot Permissions: `Connect`, `Speak` (Speak isn't strictly required since
     it won't play audio, but doesn't hurt)
   - Open the generated URL and add the bot to your server

3. **Get your voice channel ID**
   - In Discord, enable Developer Mode (User Settings → Advanced)
   - Right-click the voice channel → Copy Channel ID

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Also install `ffmpeg` on your system (discord.py's voice client needs it
   even though this bot doesn't play any audio):
   - Windows: download from ffmpeg.org and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

5. **Configure**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in:
   - `DISCORD_TOKEN` — your bot token
   - `VOICE_CHANNEL_ID` — the channel ID from step 3

6. **Run it**
   ```bash
   python bot.py
   ```

The bot will log in, join the configured voice channel, and stay connected.
A background watchdog checks every 30 seconds and rejoins if it somehow
dropped out.

## Keeping it running 24/7

Running `python bot.py` in a terminal only lasts as long as that terminal is
open, and won't survive a reboot or a crash. You need two things: an
always-on machine, and a process manager that restarts the bot if it dies.

### Where to run it

- **Free/cheap VPS**: Oracle Cloud Free Tier, Hetzner (~$4/mo), DigitalOcean
  (~$5/mo) — most reliable, full control.
- **PaaS (easiest)**: Railway, Fly.io, or Render — push your code, they keep
  it running, free tiers usually cover a small bot like this.
- **Raspberry Pi at home** — free if you already own one, just needs to stay
  powered on and connected.
- Your personal PC works too, but only if it never sleeps or shuts down —
  not recommended for real 24/7 use.

### Option A: Docker (recommended, works the same everywhere)

This repo includes a `Dockerfile` and `docker-compose.yml`. On any machine
with Docker installed:

```bash
cp .env.example .env   # fill in your token + channel ID
docker compose up -d --build
```

`restart: always` in `docker-compose.yml` means Docker restarts the bot
automatically if it crashes or the machine reboots. To check logs:

```bash
docker compose logs -f
```

To stop it:

```bash
docker compose down
```

### Option B: Bare VPS with pm2 or systemd

If you'd rather not use Docker, run it with a process manager, e.g.:

```bash
pip install pm2  # or use systemd / screen / tmux / docker
pm2 start bot.py --interpreter python3 --name voice-sitter
```

Or as a simple systemd service (Linux):

```ini
[Unit]
Description=Discord Voice Sitter Bot
After=network.target

[Service]
WorkingDirectory=/path/to/discord-voice-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
User=youruser

[Install]
WantedBy=multi-user.target
```

## Notes

- The bot self-deafens on join (`self_deaf=True`) since it isn't listening
  to anything — this reduces unnecessary bandwidth.
- It doesn't play or record any audio; it's purely a "presence" bot.
- If you ever want it to switch channels, just change `VOICE_CHANNEL_ID` in
  `.env` and restart.
