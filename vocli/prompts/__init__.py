"""Auto-import all prompt modules to register them with the MCP server."""

import importlib
from pathlib import Path

prompts_dir = Path(__file__).parent
for f in sorted(prompts_dir.glob("*.py")):
    if f.name != "__init__.py":
        importlib.import_module(f".{f.stem}", package=__name__)
