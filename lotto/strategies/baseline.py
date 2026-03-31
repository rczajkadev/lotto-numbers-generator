import random

from ..core import AbstractStrategy, LottoDrawRecord, StrategyMetadata, StrategyRegistry

_metadata = StrategyMetadata(
    requires_data=False,
)


@StrategyRegistry.register('random', _metadata)
class Baseline(AbstractStrategy):
    def __init__(self, _: dict[str, str]) -> None:
        pass

    def prepare_data(self, _: list[LottoDrawRecord]) -> None:
        pass

    def generate_numbers(self) -> list[int]:
        numbers = random.sample(range(1, self.POOL_MAX + 1), k=self.TAKE)
        numbers.sort()
        return numbers
