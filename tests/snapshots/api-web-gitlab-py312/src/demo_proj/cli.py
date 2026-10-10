"""Command line interface for demo-proj: serve the API or export its schema."""

import json
from pathlib import Path
from typing import Annotated

import typer
import uvicorn

from demo_proj import PROJECT_NAME, __version__
from demo_proj.app import create_app
from demo_proj.logging import setup_logging
from demo_proj.settings import load_settings

app = typer.Typer(help=f"{PROJECT_NAME} CLI", no_args_is_help=True)


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


@app.command()
def serve(
    env_file: Annotated[
        Path | None,
        typer.Option(
            exists=True, dir_okay=False, readable=True, help="Load a dotenv file."
        ),
    ] = None,
    host: Annotated[str, typer.Option(help="Interface to bind.")] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Port to bind.")] = 8000,
    reload: Annotated[
        bool, typer.Option(help="Restart on source changes, for development.")
    ] = False,
) -> None:
    """Serve the API with uvicorn."""
    # Fails fast on bad settings, before uvicorn starts, and sets up logging for the
    # reload supervisor, which never serves itself.
    setup_logging(load_settings(env_file=env_file).logging)
    uvicorn.run(
        # A factory by import string, which reload requires: the child imports it.
        "demo_proj.app:create_serving_app",
        factory=True,
        host=host,
        port=port,
        # Loaded into the environment, which a reload child inherits; variables that
        # are already set still win, as they do with load_settings(env_file=...).
        env_file=env_file,
        reload=reload,
        # The package only: the default, the working directory, would poll .venv too.
        reload_dirs=[str(Path(__file__).parent)] if reload else None,
        # Keeps uvicorn from replacing the handler setup_logging installed, so its
        # access and error logs come out in the application's format.
        log_config=None,
    )


@app.command()
def openapi(
    output: Annotated[
        Path | None,
        typer.Option(dir_okay=False, help="Write to this file instead of stdout."),
    ] = None,
) -> None:
    """Print the OpenAPI schema, the contract API clients are generated from."""
    schema = json.dumps(create_app().openapi(), indent=2) + "\n"
    if output is None:
        typer.echo(schema, nl=False)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        # LF on every platform, where a redirected stdout would get CRLF on Windows: a
        # committed schema must not change with the OS that generated it.
        output.write_text(schema, encoding="utf-8", newline="\n")
