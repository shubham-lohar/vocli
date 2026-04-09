"""Service tool — manage STT/TTS server processes."""

import asyncio
import shutil
import subprocess
import sys
from typing import Literal

from vocli.server import mcp


@mcp.tool()
async def service(
    action: Literal["start", "stop", "restart", "status"] = "status",
    target: Literal["all", "stt", "tts"] = "all",
) -> str:
    """Manage VOCLI STT and TTS server processes.

    Args:
        action: What to do — start, stop, restart, or check status.
        target: Which server — all, stt, or tts.

    Returns:
        Result of the action.
    """
    from vocli import config as cfg
    from vocli.clients import check_stt_health, check_tts_health

    targets = ["stt", "tts"] if target == "all" else [target]
    results = []

    for t in targets:
        if action == "status":
            if t == "stt":
                ok, info = await check_stt_health()
                results.append(f"STT: {'running' if ok else 'stopped'} ({info})")
            else:
                ok, info = await check_tts_health()
                results.append(f"TTS: {'running' if ok else 'stopped'} ({info})")

        elif action == "start":
            result = await _start_server(t)
            results.append(result)

        elif action == "stop":
            result = await _stop_server(t)
            results.append(result)

        elif action == "restart":
            await _stop_server(t)
            await asyncio.sleep(1)
            result = await _start_server(t)
            results.append(result)

    return "\n".join(results)


async def _start_server(server_type: str) -> str:
    """Start a server process in the background."""
    from vocli import config as cfg
    import importlib.resources

    if server_type == "stt":
        port = cfg.STT_PORT
        script = _get_server_script("stt_server")
        env_vars = {
            "WHISPER_PORT": str(port),
            "WHISPER_MODEL": cfg.WHISPER_MODEL,
            "WHISPER_LANGUAGE": cfg.WHISPER_LANGUAGE,
        }
    else:
        port = cfg.TTS_PORT
        script = _get_server_script("tts_server")
        env_vars = {
            "TTS_PORT": str(port),
            "TTS_ENGINE": cfg.TTS_ENGINE,
            "PIPER_MODEL": cfg.PIPER_MODEL,
        }

    if not script:
        return f"{server_type.upper()}: server script not found"

    # Check if already running
    if await _port_in_use(port):
        return f"{server_type.upper()}: already running on port {port}"

    env = {**__import__("os").environ, **env_vars}
    log_dir = cfg.VOCLI_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{server_type}.log"

    # Use python3 from PATH (where deps are installed), not sys.executable
    # (which may be the MCP server's Python without the right packages)
    python = shutil.which("python3") or sys.executable

    with open(log_file, "a") as log:
        subprocess.Popen(
            [python, str(script)],
            env=env,
            stdout=log,
            stderr=log,
        )

    # Wait briefly for startup
    await asyncio.sleep(2)
    if await _port_in_use(port):
        return f"{server_type.upper()}: started on port {port}"
    else:
        return f"{server_type.upper()}: failed to start. Check {log_file}"


async def _stop_server(server_type: str) -> str:
    """Stop a server process by finding it on its port."""
    from vocli import config as cfg
    import signal

    port = cfg.STT_PORT if server_type == "stt" else cfg.TTS_PORT

    try:
        result = await asyncio.to_thread(
            subprocess.run,
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True,
        )
        pids = result.stdout.strip().split("\n")
        pids = [p for p in pids if p]
        if not pids:
            return f"{server_type.upper()}: not running"
        for pid in pids:
            __import__("os").kill(int(pid), signal.SIGTERM)
        return f"{server_type.upper()}: stopped (pid {', '.join(pids)})"
    except Exception as e:
        return f"{server_type.upper()}: error stopping — {e}"


def _get_server_script(name: str):
    """Get path to a server script."""
    from pathlib import Path
    script = Path(__file__).parent.parent / "servers" / f"{name}.py"
    return script if script.exists() else None


async def _port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(("127.0.0.1", port))
            return True
    except (ConnectionRefusedError, OSError):
        return False
