import statistics
from collections.abc import Iterable
from dataclasses import dataclass

from .core import GameRecord, GameType


@dataclass
class BasicMetrics:
    total_draws: int
    hit_rate: float
    average_hits_per_bet: float


@dataclass
class MonetaryMetrics:
    total_winnings: float
    total_cost: float
    net_profit: float
    roi_pct: float


@dataclass
class BacktestReport:
    basic_accuracy: BasicMetrics
    monetary_metrics: MonetaryMetrics


class MetricsCalculator:
    PRIZE_TABLES = {
        GameType.LOTTO: {1: 0, 2: 0, 3: 24, 4: 200, 5: 5000, 6: 2000000},
        GameType.LOTTO_PLUS: {1: 0, 2: 0, 3: 20, 4: 180, 5: 4500, 6: 1000000},
    }
    TICKET_COSTS = {
        GameType.LOTTO: 3.0,
        GameType.LOTTO_PLUS: 1.0,
    }

    def __init__(self, records: Iterable[GameRecord]) -> None:
        self._lotto_records = [r for r in records if r.game_type == GameType.LOTTO]
        self._lotto_plus_records = [r for r in records if r.game_type == GameType.LOTTO_PLUS]

    def generate_report(self, game_type: GameType) -> BacktestReport:
        return BacktestReport(
            basic_accuracy=self.calculate_basic_metrics(game_type),
            monetary_metrics=self.calculate_monetary_metrics(game_type),
        )

    def calculate_basic_metrics(self, game_type: GameType) -> BasicMetrics:
        records = self._get_records_for_game_type(game_type)

        total_draws = len(records)
        if total_draws == 0:
            return BasicMetrics(total_draws=0, hit_rate=0, average_hits_per_bet=0)

        matches = [r.matches for r in records]
        hit_rate = sum(1 for m in matches if m >= 1) / total_draws
        average_hits = statistics.mean(matches)

        return BasicMetrics(
            total_draws=total_draws,
            hit_rate=hit_rate,
            average_hits_per_bet=average_hits,
        )

    def calculate_monetary_metrics(self, game_type: GameType) -> MonetaryMetrics:
        records = self._get_records_for_game_type(game_type)
        if not records:
            return MonetaryMetrics(
                total_winnings=0,
                total_cost=0,
                net_profit=0,
                roi_pct=0,
            )

        ticket_cost = self.TICKET_COSTS[game_type]
        winnings = [self.PRIZE_TABLES[record.game_type].get(record.matches, 0) for record in records]

        total_cost = len(records) * ticket_cost
        total_winnings = sum(winnings)
        net_profit = total_winnings - total_cost
        roi = (net_profit / total_cost) * 100 if total_cost > 0 else 0

        return MonetaryMetrics(
            total_winnings=total_winnings,
            total_cost=total_cost,
            net_profit=net_profit,
            roi_pct=roi,
        )

    def _get_records_for_game_type(self, game_type: GameType) -> list[GameRecord]:
        return self._lotto_records if game_type == GameType.LOTTO else self._lotto_plus_records
