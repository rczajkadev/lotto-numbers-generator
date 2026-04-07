from dataclasses import dataclass

from . import lotto_client
from .core import AbstractStrategy, GameRecord, GameType, LottoDrawRecord, StrategyRegistry, UnknownStrategyError
from .metrics import BacktestReport, MetricsCalculator


class StrategyParamError(ValueError):
    pass


@dataclass
class PreparedGeneration:
    numbers: list[int] | None


@dataclass
class PreparedSimulation:
    strategy_name: str
    strategy: AbstractStrategy
    data: list[LottoDrawRecord]
    total_games: int


@dataclass
class SimulationSummary:
    lotto_report: BacktestReport
    lotto_plus_report: BacktestReport


def generate_numbers(
    strategy_name: str,
    params: dict[str, str],
    date_from: str | None,
    date_to: str | None,
    top: int,
) -> PreparedGeneration:
    strategy = resolve_strategy(strategy_name, params)
    requires_data = strategy_requires_data(strategy_name)

    if requires_data:
        data = lotto_client.get_draw_results(date_from, date_to, top)

        if not data:
            return PreparedGeneration(numbers=None)
    else:
        data = []

    strategy.prepare_data(data)
    return PreparedGeneration(numbers=strategy.generate_numbers())


def prepare_simulation(
    strategy_name: str,
    params: dict[str, str],
    date_from: str | None,
    date_to: str | None,
    top: int | None,
) -> PreparedSimulation:
    strategy = resolve_strategy(strategy_name, params)
    data = lotto_client.get_draw_results(date_from, date_to, top)
    total_games = sum(1 + int(bool(record.plus_numbers)) for record in data)

    return PreparedSimulation(
        strategy_name=strategy_name,
        strategy=strategy,
        data=data,
        total_games=total_games,
    )


def build_simulation_summary(history: list[GameRecord]) -> SimulationSummary:
    metrics_calculator = MetricsCalculator(history)

    return SimulationSummary(
        lotto_report=metrics_calculator.generate_report(GameType.LOTTO),
        lotto_plus_report=metrics_calculator.generate_report(GameType.LOTTO_PLUS),
    )


def list_strategies() -> list[str]:
    return StrategyRegistry.list_strategies()


def resolve_strategy(strategy_name: str, params: dict[str, str]) -> AbstractStrategy:
    try:
        return StrategyRegistry.resolve(strategy_name, params)
    except UnknownStrategyError:
        raise
    except ValueError as exc:
        raise StrategyParamError(str(exc)) from exc


def strategy_requires_data(strategy_name: str) -> bool:
    return StrategyRegistry.requires_data(strategy_name)
