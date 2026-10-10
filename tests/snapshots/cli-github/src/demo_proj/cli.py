"""Command line interface for demo-proj."""

from typing import Annotated

import typer

from demo_proj import PROJECT_NAME, __version__
from demo_proj.logging import get_logger, setup_logging
from demo_proj.settings import Settings

app = typer.Typer(help=f"{PROJECT_NAME} CLI", no_args_is_help=True)


def configure() -> Settings:
    """Load settings, set up logging and return the settings.

    Every command calls this first. It runs in the command, not in the callback,
    because Click runs the callback before it parses the subcommand: `settings --help`
    would otherwise read and validate configuration just to print help.
    """
    settings = Settings()
    setup_logging(settings.logging)
    return settings


def _version_callback(value: bool) -> None:
    """Print the version and exit, before any subcommand is resolved."""
    if value:
        typer.echo(f"{PROJECT_NAME} {__version__}")
        raise typer.Exit


@app.callback()
def main(
    _version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,  # else no_args_is_help resolves first, before --version runs
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Run the demo-proj CLI."""


@app.command("settings")
def show_settings() -> None:
    """Print the settings the application would run with, as JSON."""
    settings = configure()
    get_logger(__name__).debug("showing settings")
    # Secret fields must be SecretStr: it dumps masked, where a plain str would leak.
    typer.echo(settings.model_dump_json(indent=2))
