"""VOCLI CLI entry point."""

import click


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """VOCLI — local voice layer for AI coding tools."""
    if ctx.invoked_subcommand is None:
        # Default: run MCP server
        from vocli.server import main as run_server
        run_server()


@main.command()
def serve():
    """Run VOCLI as MCP server (stdio transport)."""
    from vocli.server import main as run_server
    run_server()
