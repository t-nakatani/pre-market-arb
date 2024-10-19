from abc import ABC, abstractmethod


class ISubStrategy(ABC):
    @abstractmethod
    def determine_limit_price(self, best_prices) -> float:
        pass
