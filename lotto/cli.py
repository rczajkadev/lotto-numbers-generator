from datetime import datetime
from typing import Annotated

import typer
from rich.columns import Columns
from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text

from . import lotto_client
from .core import AbstractStrategy, GameType, StrategyRegistry, UnknownStrategyError
from .metrics import BacktestReport, MetricsCalculator
from .settings import config
from .simulation import BacktestEngine
from .visualisation import visualise_results

_app = typer.Typer(name=config.app.name, add_completion=False, no_args_is_help=True)
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


def _is_date_str_valid(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, config.app.date_format)
        return True
    except ValueError:
        return False


def _validate_date_options(date_from: str | None, date_to: str | None) -> None:
    if date_from and not _is_date_str_valid(date_from):
        raise typer.BadParameter(f'Invalid date format for --date-from. Expected format: {config.app.date_format}')
    if date_to and not _is_date_str_valid(date_to):
        raise typer.BadParameter(f'Invalid date format for --date-to. Expected format: {config.app.date_format}')


def _parse_params(params: list[str] | None) -> dict[str, str]:
    if params is None:
        return {}

    parsed_params: dict[str, str] = {}

    for param_item in params:
        name, separator, value = param_item.partition('=')

        if separator != '=' or not name:
            raise typer.BadParameter('Parameters must use the format name=value.', param_hint='--param')

        if name in parsed_params:
            raise typer.BadParameter(f'Duplicate parameter: {name}', param_hint='--param')

        parsed_params[name] = value

    return parsed_params


def _resolve_strategy(strategy_name: str, params: dict[str, str]) -> AbstractStrategy:
    try:
        return StrategyRegistry.resolve(strategy_name, params)
    except UnknownStrategyError as exc:
        raise typer.BadParameter(str(exc), param_hint='--strategy') from exc
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint='--param') from exc


def _strategy_requires_data(strategy_name: str) -> bool:
    try:
        return StrategyRegistry.requires_data(strategy_name)
    except UnknownStrategyError as exc:
        raise typer.BadParameter(str(exc), param_hint='--strategy') from exc


def _get_metrics_table(title: str, report: BacktestReport) -> Table:
    table = Table(title=Text(title, style='bold'))

    table.add_column(Text('Metric', justify='center'), no_wrap=True)
    table.add_column('Value', justify='right', style=_color)

    ba = report.basic_accuracy

    table.add_row('total_draws', str(ba.total_draws))
    table.add_row('hit_rate', f'{ba.hit_rate:.2f}')
    table.add_row('average_hits_per_bet', f'{ba.average_hits_per_bet:.2f}')
    table.add_section()

    mm = report.monetary_metrics

    table.add_row('total_winnings', f'{mm.total_winnings:.2f}')
    table.add_row('total_cost', f'{mm.total_cost:.2f}')
    table.add_row('net_profit', f'{mm.net_profit:.2f}')
    table.add_row('roi_pct', f'{mm.roi_pct:.2f}')

    return table


@_app.command(name='simulate')
def run_simulation(
    strategy_name: Annotated[str, typer.Option('--strategy', '-s')],
    params: Annotated[list[str] | None, typer.Option('--param', '-p')] = None,
    date_from: Annotated[str | None, typer.Option('--date-from')] = None,
    date_to: Annotated[str | None, typer.Option('--date-to')] = None,
    top: Annotated[int | None, typer.Option('--top', min=1)] = None,
) -> None:
    _validate_date_options(date_from, date_to)
    params_dict = _parse_params(params)
    strategy = _resolve_strategy(strategy_name, params_dict)

    with _console.status('Fetching data', spinner=_spinner_type, spinner_style=_color):
        data = lotto_client.get_draw_results(date_from, date_to, top)

    if not data:
        _console.print('No draw results found for the selected filters.', style='yellow')
        return

    backtest = BacktestEngine(strategy)

    results_iterator = backtest.results_gen(data)
    total_games = sum(1 + int(bool(record.plus_numbers)) for record in data)
    results = []

    with _progress:
        task = _progress.add_task('Backtest:', total=total_games)

        for result in results_iterator:
            results.append(result)
            _progress.advance(task)

    metrics_calculator = MetricsCalculator(backtest.history)
    lotto_metrics = metrics_calculator.generate_report(GameType.LOTTO)
    lotto_plus_metrics = metrics_calculator.generate_report(GameType.LOTTO_PLUS)

    lotto_table = _get_metrics_table('Lotto - metrics', lotto_metrics)
    lotto_plus_table = _get_metrics_table('Lotto Plus - metrics', lotto_plus_metrics)

    _console.print()
    _console.print(Columns([lotto_table, lotto_plus_table], padding=(0, 2)))
    _console.print()

    visualise_results(results, strategy_name)


@_app.command(name='strategies')
def list_strategies() -> None:
    strategies = StrategyRegistry.list_strategies()

    _console.print('Available Strategies:', style='bold')

    for strategy in strategies:
        _console.print(f'- {strategy}')


@_app.command(name='generate')
def generate_numbers(
    strategy_name: Annotated[str, typer.Option('--strategy', '-s')],
    params: Annotated[list[str] | None, typer.Option('--param', '-p')] = None,
    date_from: Annotated[str | None, typer.Option('--date-from')] = None,
    date_to: Annotated[str | None, typer.Option('--date-to')] = None,
    top: Annotated[int, typer.Option('--top', min=1)] = 100,
) -> None:
    _validate_date_options(date_from, date_to)

    params_dict = _parse_params(params)
    requires_data = _strategy_requires_data(strategy_name)
    strategy = _resolve_strategy(strategy_name, params_dict)

    if requires_data:
        with _console.status('Fetching data', spinner=_spinner_type, spinner_style=_color):
            data = lotto_client.get_draw_results(date_from, date_to, top)

        if not data:
            _console.print('No draw results found for the selected filters.', style='yellow')
            return
    else:
        data = []

    strategy.prepare_data(data)
    numbers = strategy.generate_numbers()

    _console.print(f'Generated numbers: [bold green]{", ".join(map(str, numbers))}[/]')


def run_typer_app() -> None:
    _app()
