from datetime import datetime
from typing import Annotated

import typer
from rich.columns import Columns
from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text

from . import services
from .core import UnknownStrategyError
from .metrics import BacktestReport
from .settings import config
from .simulation import BacktestEngine
from .visualisation import visualise_results

_app = typer.Typer(
    name=config.app.name,
    add_completion=False,
    invoke_without_command=True,
    help='Generate numbers by default when no command is provided.',
)
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


def _map_service_error(exc: Exception) -> typer.BadParameter:
    if isinstance(exc, UnknownStrategyError):
        return typer.BadParameter(str(exc), param_hint='--strategy')
    if isinstance(exc, services.StrategyParamError):
        return typer.BadParameter(str(exc), param_hint='--param')
    raise TypeError(f'Unsupported service exception type: {type(exc).__name__}')


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


@_app.callback()
def run_default_command(
    ctx: typer.Context,
    strategy_name: Annotated[str | None, typer.Option('--strategy', '-s')] = None,
    params: Annotated[list[str] | None, typer.Option('--param', '-p')] = None,
    date_from: Annotated[str | None, typer.Option('--date-from')] = None,
    date_to: Annotated[str | None, typer.Option('--date-to')] = None,
    top: Annotated[int, typer.Option('--top', min=1)] = 100,
) -> None:
    if ctx.invoked_subcommand is not None:
        return

    if strategy_name is None:
        if params is None and date_from is None and date_to is None and top == 100:
            _console.print(ctx.get_help(), end='')
            raise typer.Exit()

        raise typer.BadParameter('Option --strategy is required in default generate mode.', param_hint='--strategy')

    _validate_date_options(date_from, date_to)
    params_dict = _parse_params(params)

    try:
        requires_data = services.strategy_requires_data(strategy_name)
    except UnknownStrategyError as exc:
        raise _map_service_error(exc) from exc

    try:
        if requires_data:
            with _console.status('Fetching data', spinner=_spinner_type, spinner_style=_color):
                generation = services.generate_numbers(strategy_name, params_dict, date_from, date_to, top)
        else:
            generation = services.generate_numbers(strategy_name, params_dict, date_from, date_to, top)
    except (UnknownStrategyError, services.StrategyParamError) as exc:
        raise _map_service_error(exc) from exc

    if generation.numbers is None:
        _console.print('No draw results found for the selected filters.', style='yellow')
        return

    _console.print(f'Generated numbers: [bold green]{", ".join(map(str, generation.numbers))}[/]')


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

    try:
        with _console.status('Fetching data', spinner=_spinner_type, spinner_style=_color):
            prepared_simulation = services.prepare_simulation(strategy_name, params_dict, date_from, date_to, top)
    except (UnknownStrategyError, services.StrategyParamError) as exc:
        raise _map_service_error(exc) from exc

    if not prepared_simulation.data:
        _console.print('No draw results found for the selected filters.', style='yellow')
        return

    backtest = BacktestEngine(prepared_simulation.strategy)

    results_iterator = backtest.results_gen(prepared_simulation.data)
    results = []

    with _progress:
        task = _progress.add_task('Backtest:', total=prepared_simulation.total_games)

        for result in results_iterator:
            results.append(result)
            _progress.advance(task)

    summary = services.build_simulation_summary(backtest.history)

    lotto_table = _get_metrics_table('Lotto - metrics', summary.lotto_report)
    lotto_plus_table = _get_metrics_table('Lotto Plus - metrics', summary.lotto_plus_report)

    _console.print()
    _console.print(Columns([lotto_table, lotto_plus_table], padding=(0, 2)))
    _console.print()

    visualise_results(results, prepared_simulation.strategy_name)


@_app.command(name='strategies')
def list_strategies() -> None:
    strategies = services.list_strategies()

    _console.print('Available Strategies:', style='bold')

    for strategy in strategies:
        _console.print(f'- {strategy}')


def run_typer_app() -> None:
    _app()
