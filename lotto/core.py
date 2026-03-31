from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto


class GameType(Enum):
    LOTTO = auto()
    LOTTO_PLUS = auto()


@dataclass
class LottoDrawRecord:
    draw_date: date
    lotto_numbers: list[int]
    plus_numbers: list[int]


@dataclass
class GameRecord:
    game_type: GameType
    draw_date: date
    draw_result: list[int]
    generated_numbers: list[int]
    matches: int


class AbstractStrategy(ABC):
    POOL_MAX = 49
    TAKE = 6

    @abstractmethod
    def prepare_data(self, data: list[LottoDrawRecord]) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_numbers(self) -> list[int]:
        raise NotImplementedError


@dataclass
class StrategyMetadata:
    requires_data: bool = True
    has_params: bool = True


class StrategyRegistry:
    _registry: dict[str, tuple[type[AbstractStrategy], StrategyMetadata]] = {}

    @classmethod
    def register(cls, name: str, metadata: StrategyMetadata | None = None) -> callable:
        def wrapper(strategy_type: type[AbstractStrategy]) -> type[AbstractStrategy]:
            cls._registry[name] = strategy_type, metadata or StrategyMetadata()
            return strategy_type

        return wrapper

    @classmethod
    def requires_data(cls, name: str) -> bool:
        _, metadata = cls._get_strategy_entry(name)
        return metadata.requires_data

    @classmethod
    def list_strategies(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def resolve(cls, name: str, params: dict[str, str]) -> AbstractStrategy:
        strategy_type, metadata = cls._get_strategy_entry(name)
        return strategy_type(params) if metadata.has_params else strategy_type()

    @classmethod
    def _get_strategy_entry(cls, name: str) -> tuple[type[AbstractStrategy], StrategyMetadata]:
        entry = cls._registry.get(name)

        if entry is None:
            raise ValueError(f'Unknown strategy: {name}')

        return entry
