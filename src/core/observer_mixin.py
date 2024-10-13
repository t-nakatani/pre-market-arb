from abc import ABC, abstractmethod

from core.trading_strategy import StrategyChoice


class MarketStatusObserverMixin(ABC):
    @abstractmethod
    async def on_market_status_changed(self, strategy_choice: StrategyChoice):
        pass

class SettleObserverMixin(ABC):
    @abstractmethod
    async def on_order_filled(self):
        pass
