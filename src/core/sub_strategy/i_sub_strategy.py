from abc import ABC, abstractmethod

from core.types import BestPrices, Side


class ISubStrategy(ABC):
    @abstractmethod
    def determine_limit_price(self, best_prices: BestPrices, side: Side, price_precision: float) -> float:
        pass
