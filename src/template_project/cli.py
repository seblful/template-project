"""Command line interface for template-project."""

from typing import Optional

import typer

from config import get_settings, setup_logging

app = typer.Typer(
    help="Template Project CLI - A modern Python template following best practices",
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
    """Template Project CLI - A modern Python template following best practices."""
    # Setup logging
    settings = get_settings()
    if debug:
        settings.debug = True

    if log_level:
        settings.log_level = log_level

    setup_logging(log_level=log_level or settings.log_level)

    if settings.debug:
        typer.echo(f"Debug mode enabled")
        typer.echo(f"Environment: {settings.environment}")


@app.command()
def hello() -> None:
    """Say hello to the user."""
    settings = get_settings()
    typer.echo(f"Hello from {settings.app_name}!")
    typer.echo(f"Version: {settings.app_version}")
    typer.echo(f"Environment: {settings.environment}")


@app.command()
def info() -> None:
    """Display project information."""
    settings = get_settings()

    typer.echo("=" * 50)
    typer.echo(f"{settings.app_name} - Project Information")
    typer.echo("=" * 50)
    typer.echo(f"Version: {settings.app_version}")
    typer.echo(f"Environment: {settings.environment}")
    typer.echo(f"Debug Mode: {settings.debug}")
    typer.echo(f"Log Level: {settings.log_level}")
    typer.echo(f"Base Directory: {settings.base_dir}")
    typer.echo(f"Data Directory: {settings.data_dir}")
    typer.echo(f"Logs Directory: {settings.logs_dir}")
    typer.echo(f"Models Directory: {settings.models_dir}")
    typer.echo("=" * 50)


@app.command()
def init() -> None:
    """Initialize project directories."""
    settings = get_settings()
    settings.ensure_directories()

    typer.echo("Project directories initialized:")
    typer.echo(f"  Data: {settings.data_dir}")
    typer.echo(f"  Logs: {settings.logs_dir}")
    typer.echo(f"  Models: {settings.models_dir}")


if __name__ == "__main__":
    app()
