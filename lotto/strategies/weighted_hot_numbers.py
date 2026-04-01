from collections import Counter

from ..core import AbstractStrategy, LottoDrawRecord, StrategyMetadata, StrategyRegistry

_default_params = {
    'lookback': '100',
}


_metadata = StrategyMetadata()


@StrategyRegistry.register('weighted-hot-numbers', _metadata)
class WeightedHotNumbers(AbstractStrategy):
    def __init__(self, params: dict[str, str]) -> None:
        self._lookback = int(params.get('lookback', _default_params['lookback']))

        if self._lookback < 0:
            raise ValueError('Parameter lookback must be a non-negative integer.')

        self._data: list[LottoDrawRecord] = []

    def prepare_data(self, data: list[LottoDrawRecord]) -> None:
        self._data = data

    def generate_numbers(self) -> list[int]:
        draws = self._data[-self._lookback :] if self._lookback else self._data
        counter = Counter()

        for weight, record in enumerate(draws, start=1):
            for number in record.lotto_numbers:
                if 1 <= number <= self.POOL_MAX:
                    counter[number] += weight

        ranked = sorted(range(1, self.POOL_MAX + 1), key=lambda number: (-counter.get(number, 0), number))
        pick = ranked[: self.TAKE]
        pick.sort()

        return pick
