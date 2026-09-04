from ..core import AbstractRankedStrategy, AbstractStrategy, LottoDrawRecord, StrategyMetadata, StrategyRegistry
from .decay_hot_numbers import DecayHotNumbers
from .overdue_numbers import OverdueNumbers
from .rising_numbers import RisingNumbers

_metadata = StrategyMetadata()


def _remap_params(params: dict[str, str], mapping: dict[str, str]) -> dict[str, str]:
    return {target: params[source] for source, target in mapping.items() if source in params}


@StrategyRegistry.register('balanced-mix', _metadata)
class BalancedMix(AbstractStrategy):
    def __init__(self, params: dict[str, str]) -> None:
        decay = DecayHotNumbers(
            _remap_params(
                params,
                {
                    'decay_lookback': 'lookback',
                    'decay': 'decay',
                },
            )
        )
        rising = RisingNumbers(
            _remap_params(
                params,
                {
                    'rising_short_lookback': 'short_lookback',
                    'rising_long_lookback': 'long_lookback',
                },
            )
        )
        overdue = OverdueNumbers(
            _remap_params(
                params,
                {
                    'overdue_lookback': 'lookback',
                },
            )
        )

        self._strategies: tuple[AbstractRankedStrategy, ...] = (decay, rising, overdue)
        self._selection_order = (decay, rising, overdue, overdue, rising, decay)

    def prepare_data(self, data: list[LottoDrawRecord]) -> None:
        for strategy in self._strategies:
            strategy.prepare_data(data)

    def generate_numbers(self) -> list[int]:
        rankings = {strategy: strategy.rank_numbers() for strategy in self._strategies}
        selected: set[int] = set()

        for strategy in self._selection_order:
            number = next(number for number in rankings[strategy] if number not in selected)
            selected.add(number)

        return sorted(selected)
