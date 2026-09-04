from ..core import AbstractRankedStrategy, LottoDrawRecord, StrategyMetadata, StrategyRegistry
from ._params import parse_non_negative_int_param

_default_params = {
    'lookback': '100',
}


_metadata = StrategyMetadata()


@StrategyRegistry.register('overdue-numbers', _metadata)
class OverdueNumbers(AbstractRankedStrategy):
    def __init__(self, params: dict[str, str]) -> None:
        self._lookback = parse_non_negative_int_param(params, 'lookback', _default_params['lookback'])
        self._data: list[LottoDrawRecord] = []

    def prepare_data(self, data: list[LottoDrawRecord]) -> None:
        self._data = data

    def rank_numbers(self) -> list[int]:
        draws = self._data[-self._lookback :] if self._lookback else self._data
        last_seen_index: dict[int, int] = {}

        for index, record in enumerate(draws):
            for number in record.lotto_numbers:
                if 1 <= number <= self.POOL_MAX:
                    last_seen_index[number] = index

        return sorted(
            range(1, self.POOL_MAX + 1),
            key=lambda number: (number in last_seen_index, last_seen_index.get(number, -1), number),
        )
