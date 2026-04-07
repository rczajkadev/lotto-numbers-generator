from collections.abc import Callable, Iterator
from contextlib import contextmanager

import typer
from rich.columns import Columns
from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text

from ..metrics import BacktestReport
from ..services import SimulationSummary

_console = Console()
_spinner_type = 'arc'
_color = 'bright_cyan'

_progress = Progress(
    TextColumn('{task.description}'),
    BarColumn(style=Style(), complete_style=_color, finished_style=_color, pulse_style=_color),
    TaskProgressColumn(text_format='{task.percentage:>3.0f}%'),
    console=_console,
    transient=True,
)


@contextmanager
def fetching_status() -> Iterator[None]:
    with _console.status('Fetching data', spinner=_spinner_type, spinner_style=_color):
        yield


@contextmanager
def backtest_progress(total_games: int) -> Iterator[Callable[[], None]]:
    with _progress:
        task = _progress.add_task('Backtest:', total=total_games)

        def advance() -> None:
            _progress.advance(task)

        yield advance


def show_root_help_and_exit(ctx: typer.Context) -> None:
    _console.print(ctx.get_help(), end='')
    raise typer.Exit()


def show_no_draw_results() -> None:
    _console.print('No draw results found for the selected filters.', style='yellow')


def render_generated_numbers(numbers: list[int]) -> None:
    _console.print(f'Generated numbers: [bold green]{", ".join(map(str, numbers))}[/]')


def render_strategy_list(strategies: list[str]) -> None:
    _console.print('Available Strategies:', style='bold')

    for strategy in strategies:
        _console.print(f'- {strategy}')


def render_simulation_summary(summary: SimulationSummary) -> None:
    lotto_table = _get_metrics_table('Lotto - metrics', summary.lotto_report)
    lotto_plus_table = _get_metrics_table('Lotto Plus - metrics', summary.lotto_plus_report)

    _console.print()
    _console.print(Columns([lotto_table, lotto_plus_table], padding=(0, 2)))
    _console.print()


def _get_metrics_table(title: str, report: BacktestReport) -> Table:
    table = Table(title=Text(title, style='bold'))

    table.add_column(Text('Metric', justify='center'), no_wrap=True)
    table.add_column('Value', justify='right', style=_color)

    basic_accuracy = report.basic_accuracy
    monetary_metrics = report.monetary_metrics

    table.add_row('total_draws', str(basic_accuracy.total_draws))
    table.add_row('hit_rate', f'{basic_accuracy.hit_rate:.2f}')
    table.add_row('average_hits_per_bet', f'{basic_accuracy.average_hits_per_bet:.2f}')
    table.add_section()
    table.add_row('total_winnings', f'{monetary_metrics.total_winnings:.2f}')
    table.add_row('total_cost', f'{monetary_metrics.total_cost:.2f}')
    table.add_row('net_profit', f'{monetary_metrics.net_profit:.2f}')
    table.add_row('roi_pct', f'{monetary_metrics.roi_pct:.2f}')

    return table
