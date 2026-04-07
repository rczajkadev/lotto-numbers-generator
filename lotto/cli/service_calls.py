from collections.abc import Callable

import typer

from .. import services
from ..core import GameRecord, UnknownStrategyError
from ..simulation import BacktestEngine


def get_strategy_requires_data(strategy_name: str) -> bool:
    try:
        return services.strategy_requires_data(strategy_name)
    except UnknownStrategyError as exc:
        raise _map_service_error(exc) from exc


def generate_numbers(
    strategy_name: str,
    params: dict[str, str],
    date_from: str | None,
    date_to: str | None,
    top: int,
) -> services.PreparedGeneration:
    try:
        return services.generate_numbers(strategy_name, params, date_from, date_to, top)
    except (UnknownStrategyError, services.StrategyParamError) as exc:
        raise _map_service_error(exc) from exc


def prepare_simulation(
    strategy_name: str,
    params: dict[str, str],
    date_from: str | None,
    date_to: str | None,
    top: int | None,
) -> services.PreparedSimulation:
    try:
        return services.prepare_simulation(strategy_name, params, date_from, date_to, top)
    except (UnknownStrategyError, services.StrategyParamError) as exc:
        raise _map_service_error(exc) from exc


def run_backtest(
    prepared_simulation: services.PreparedSimulation,
    on_result: Callable[[], None],
) -> tuple[list[GameRecord], services.SimulationSummary]:
    backtest = BacktestEngine(prepared_simulation.strategy)
    results: list[GameRecord] = []

    for result in backtest.results_gen(prepared_simulation.data):
        results.append(result)
        on_result()

    summary = services.build_simulation_summary(backtest.history)
    return results, summary


def list_strategies() -> list[str]:
    return services.list_strategies()


def _map_service_error(exc: Exception) -> typer.BadParameter:
    if isinstance(exc, UnknownStrategyError):
        return typer.BadParameter(str(exc), param_hint='--strategy')
    if isinstance(exc, services.StrategyParamError):
        return typer.BadParameter(str(exc), param_hint='--param')
    raise TypeError(f'Unsupported service exception type: {type(exc).__name__}')
