from collections import Counter

from ..core import AbstractRankedStrategy, LottoDrawRecord, StrategyMetadata, StrategyRegistry
from ._params import parse_float_between_param, parse_non_negative_int_param

_default_params = {
    'lookback': '100',
    'decay': '0.95',
}


_metadata = StrategyMetadata()


@StrategyRegistry.register('decay-hot-numbers', _metadata)
class DecayHotNumbers(AbstractRankedStrategy):
    def __init__(self, params: dict[str, str]) -> None:
        self._lookback = parse_non_negative_int_param(params, 'lookback', _default_params['lookback'])
        self._decay = parse_float_between_param(params, 'decay', _default_params['decay'], 0, 1)
        self._data: list[LottoDrawRecord] = []

    def prepare_data(self, data: list[LottoDrawRecord]) -> None:
        self._data = data

    def rank_numbers(self) -> list[int]:
        draws = self._data[-self._lookback :] if self._lookback else self._data
        counter = Counter()

        for age, record in enumerate(reversed(draws)):
            weight = self._decay**age

            for number in record.lotto_numbers:
                if 1 <= number <= self.POOL_MAX:
                    counter[number] += weight

        return sorted(range(1, self.POOL_MAX + 1), key=lambda number: (-counter.get(number, 0), number))
