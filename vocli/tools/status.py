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

    # Audio devices
    try:
        import sounddevice as sd
        default_in = sd.query_devices(kind='input')
        default_out = sd.query_devices(kind='output')
        configured_in = conf.get("input_device", "default")
        configured_out = conf.get("output_device", "default")
        lines.append(f"Input device: {default_in['name']} (configured: {configured_in})")
        lines.append(f"Output device: {default_out['name']} (configured: {configured_out})")
    except Exception:
        lines.append("Audio devices: unable to query")

    # Hooks
    hooks = conf.get("hooks", {})
    lines.append(f"Auto-approve tools: {'enabled' if hooks.get('auto_approve') else 'disabled'}")

    return "\n".join(lines)
