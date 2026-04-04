"""Command line interface for {{ project_name }}."""

from typing import Optional

import typer

from {{ package_name }}.settings import settings
from {{ package_name }}.logging import setup_logging

app = typer.Typer(
    help="{{ project_name }} CLI - A modern Python project following best practices",
    add_completion=False,
)


@app.callback()
def main(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    log_level: Optional[str] = typer.Option(
        None,
        "--log-level",
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
) -> None:
    """{{ project_name }} CLI - A modern Python project following best practices."""
    if debug:
        settings.app.debug = True

    if log_level:
        settings.logging.log_level = log_level

    setup_logging(log_level=log_level or settings.logging.log_level)

    if settings.app.debug:
        typer.echo("Debug mode enabled")
        typer.echo(f"Environment: {settings.app.environment}")


@app.command()
def hello() -> None:
    """Say hello to the user."""
    typer.echo(f"Hello from {settings.app.app_name}!")
    typer.echo(f"Version: {settings.app.app_version}")
    typer.echo(f"Environment: {settings.app.environment}")


@app.command()
def info() -> None:
    """Display project information."""
    typer.echo("=" * 50)
    typer.echo(f"{settings.app.app_name} - Project Information")
    typer.echo("=" * 50)
    typer.echo(f"Version: {settings.app.app_version}")
    typer.echo(f"Environment: {settings.app.environment}")
    typer.echo(f"Debug Mode: {settings.app.debug}")
    typer.echo(f"Log Level: {settings.logging.log_level}")
    typer.echo(f"Base Directory: {settings.paths.base_dir}")
    typer.echo(f"Data Directory: {settings.paths.data_dir}")
    typer.echo(f"Logs Directory: {settings.paths.logs_dir}")
    typer.echo("=" * 50)


@app.command()
def init() -> None:
    """Initialize project directories."""
    for dir_path in [settings.paths.data_dir, settings.paths.logs_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    typer.echo("Project directories initialized:")
    typer.echo(f"  Data: {settings.paths.data_dir}")
    typer.echo(f"  Logs: {settings.paths.logs_dir}")


if __name__ == "__main__":
    app()
