"""Config prompt — personalize VOCLI settings, usable anytime."""

from vocli.server import mcp


@mcp.prompt()
def config() -> str:
    """Configure VOCLI — set or change assistant name, user name, and preferences."""
    from vocli import config as cfg

    existing = cfg.get_config()

    if existing.get("assistant_name"):
        return f"""VOCLI is already configured:

- Assistant name: {existing['assistant_name']}
- User name: {existing.get('user_name', 'not set')}
- Auto-approve tools: {'enabled' if existing.get('hooks', {}).get('auto_approve') else 'disabled'}
- Notification chime: {'enabled' if existing.get('hooks', {}).get('notify_chime') else 'disabled'}

Ask the user what they'd like to change. They can update any setting individually — no need to redo everything.

To update, read the current config from `~/.vocli/config.json`, modify the relevant field, and write it back.

If they change auto-approve, update the permissions in `~/.claude/settings.json` accordingly.

Confirm the change and let them know they can start talking with `/vocli:talk`."""

    return """You are helping the user set up VOCLI for the first time.

Ask these questions one at a time. Wait for each answer before asking the next:

1. **"What should I be called?"** — The assistant's name (e.g., "Jarvis", "Nova", "Friday").

2. **"What should I call you?"** — The user's preferred name (e.g., their first name, "Boss", "Captain").

3. **"Should I auto-approve voice tools?"** — No permission prompts when using talk/status/service. Recommend: yes. (yes/no)

4. **"Enable notification chime when tasks complete?"** — Play a sound when Claude finishes a long task. (yes/no)

After collecting all answers, save the config:

```python
import json
from pathlib import Path

config = {
    "assistant_name": "<their answer>",
    "user_name": "<their answer>",
    "hooks": {
        "auto_approve": True/False,
        "notify_chime": True/False
    }
}

config_dir = Path.home() / ".vocli"
config_dir.mkdir(parents=True, exist_ok=True)
with open(config_dir / "config.json", "w") as f:
    json.dump(config, f, indent=2)
```

If auto-approve is enabled, add vocli tools to the allow list in `~/.claude/settings.json` under `permissions.allow`:
- `mcp__plugin_vocli_vocli__talk`

Confirm setup is complete. STT and TTS servers start automatically when they use `/vocli:talk` — no manual step needed."""
