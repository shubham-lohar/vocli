# VOCLI

**Local voice layer for AI coding tools**

Talk to Claude Code with your voice. 100% local, 100% private — no audio leaves your machine.

## Install

### Option 1: Claude Code Marketplace

```
/plugin marketplace add shubham-lohar/vocli
/plugin install vocli@vocli
/vocli:install
/vocli:talk
```

### Option 2: Manual Install

```bash
# Install UV package manager (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add VOCLI to Claude Code
claude mcp add --scope user vocli -- uvx --refresh vocli

# Restart Claude Code, then:
/vocli:install    # installs whisper, piper, models
/vocli:talk       # start talking
```

## What It Does

- **You speak** — mic records, faster-whisper transcribes locally
- **Claude responds** — text sent to Piper TTS, plays through your speakers
- **Fully offline** — after initial model download, no internet needed
- **Personalized** — set your name and the assistant's name via `/vocli:config`

## Slash Commands

| Command | Description |
|---------|-------------|
| `/vocli:install` | Install dependencies, download models, configure |
| `/vocli:config` | Change assistant name, your name, preferences |
| `/vocli:talk` | Start a voice conversation |

## How It Works

```
You speak → Mic → faster-whisper (STT) → Text to Claude
Claude responds → Piper TTS → Audio plays through speakers
```

VOCLI runs as an MCP server with three tools:
- `talk` — speak + listen (auto-starts STT/TTS servers)
- `status` — check server health
- `service` — manage STT/TTS servers

## Requirements

- Python 3.10+
- macOS (Apple Silicon or Intel) or Linux
- ffmpeg (`brew install ffmpeg`)
- ~700MB disk space for models

## Architecture

```
┌─────────────────────────────────┐
│         VOCLI MCP Server        │
│  (FastMCP, stdio transport)     │
│                                 │
│  Tools: talk, status, service   │
│  Prompts: install, config, talk │
└──────┬──────────────┬───────────┘
       │              │
 ┌─────▼─────┐ ┌─────▼──────┐
 │ STT Server │ │ TTS Server │
 │ port 2022  │ │ port 8880  │
 │ faster-    │ │ Piper /    │
 │ whisper    │ │ macOS say  │
 └────────────┘ └────────────┘
```

## License

MIT
