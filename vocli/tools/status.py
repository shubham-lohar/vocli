"""Status tool — health check for STT/TTS servers and VOCLI config."""

from vocli.server import mcp


@mcp.tool()
async def status() -> str:
    """Check health of VOCLI services and configuration.

    Returns a summary of STT server, TTS server, and VOCLI config state.
    """
    from vocli.clients import check_stt_health, check_tts_health
    from vocli import config as cfg

    lines = ["## VOCLI Status\n"]

    # STT server
    stt_ok, stt_info = await check_stt_health()
    if stt_ok:
        lines.append(f"STT server: running ({stt_info})")
    else:
        lines.append(f"STT server: not responding ({stt_info})")

    # TTS server
    tts_ok, tts_info = await check_tts_health()
    if tts_ok:
        lines.append(f"TTS server: running ({tts_info})")
    else:
        lines.append(f"TTS server: not responding ({tts_info})")

    # Config
    conf = cfg.get_config()
    if conf.get("assistant_name"):
        lines.append(f"Assistant name: {conf['assistant_name']}")
        lines.append(f"User name: {conf.get('user_name', 'not set')}")
    else:
        lines.append("Config: not initialized. Run /vocli:config")

    # Hooks
    hooks = conf.get("hooks", {})
    lines.append(f"Auto-approve tools: {'enabled' if hooks.get('auto_approve') else 'disabled'}")
    lines.append(f"Notification chime: {'enabled' if hooks.get('notify_chime') else 'disabled'}")

    return "\n".join(lines)
