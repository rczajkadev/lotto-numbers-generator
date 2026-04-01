from ..core import AbstractStrategy, LottoDrawRecord, StrategyMetadata, StrategyRegistry

_metadata = StrategyMetadata(
    requires_data=False,
)


@StrategyRegistry.register('manual', _metadata)
class ManualStrategy(AbstractStrategy):
    def __init__(self, params: dict[str, str]) -> None:
        numbers_param = params.get('numbers')

        if numbers_param is None:
            raise ValueError('Parameter numbers is required.')

        raw_numbers = [item.strip() for item in numbers_param.split(',')]

        if len(raw_numbers) != self.TAKE:
            raise ValueError(f'Parameter numbers must contain exactly {self.TAKE} numbers.')

        try:
            numbers = [int(number) for number in raw_numbers]
        except ValueError as exc:
            raise ValueError('Parameter numbers must contain integers only.') from exc

        if len(set(numbers)) != self.TAKE:
            raise ValueError('Parameter numbers must not contain duplicates.')

        if any(number < 1 or number > self.POOL_MAX for number in numbers):
            raise ValueError(f'Parameter numbers must be in range 1..{self.POOL_MAX}.')

        self._numbers = sorted(numbers)

    def prepare_data(self, _: list[LottoDrawRecord]) -> None:
        pass

    def generate_numbers(self) -> list[int]:
        return list(self._numbers)
