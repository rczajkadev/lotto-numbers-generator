from collections import Counter

from ..core import AbstractRankedStrategy, LottoDrawRecord, StrategyMetadata, StrategyRegistry
from ._params import parse_positive_int_param

_default_params = {
    'short_lookback': '20',
    'long_lookback': '100',
}


_metadata = StrategyMetadata()


@StrategyRegistry.register('rising-numbers', _metadata)
class RisingNumbers(AbstractRankedStrategy):
    def __init__(self, params: dict[str, str]) -> None:
        self._short_lookback = parse_positive_int_param(
            params,
            'short_lookback',
            _default_params['short_lookback'],
        )
        self._long_lookback = parse_positive_int_param(
            params,
            'long_lookback',
            _default_params['long_lookback'],
        )

        if self._short_lookback >= self._long_lookback:
            raise ValueError('Parameter short_lookback must be less than long_lookback.')

        self._data: list[LottoDrawRecord] = []

    def prepare_data(self, data: list[LottoDrawRecord]) -> None:
        self._data = data

    def rank_numbers(self) -> list[int]:
        long_draws = self._data[-self._long_lookback :]
        short_draws = long_draws[-self._short_lookback :]

        long_counter = Counter()
        short_counter = Counter()

        for record in long_draws:
            long_counter.update([n for n in record.lotto_numbers if 1 <= n <= self.POOL_MAX])

        for record in short_draws:
            short_counter.update([n for n in record.lotto_numbers if 1 <= n <= self.POOL_MAX])

        long_draws_count = max(len(long_draws), 1)
        short_draws_count = max(len(short_draws), 1)

        return sorted(
            range(1, self.POOL_MAX + 1),
            key=lambda number: (
                -(short_counter.get(number, 0) * long_draws_count - long_counter.get(number, 0) * short_draws_count),
                -short_counter.get(number, 0),
                long_counter.get(number, 0),
                number,
            ),
        )
