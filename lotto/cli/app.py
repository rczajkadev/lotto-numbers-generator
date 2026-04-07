import typer

from ..settings import config
from .commands import register_commands

_app = typer.Typer(
    name=config.app.name,
    add_completion=False,
    invoke_without_command=True,
    help='Generate numbers by default when no command is provided.',
    rich_markup_mode=None,
)

register_commands(_app)


def run_cli_app() -> None:
    _app()
