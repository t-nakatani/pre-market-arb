import asyncio

from core.notifier import Notifier
from core.observer_pattern.i_observer_mixin import IMarketStatusObserverMixin
from core.orderbook_searcher import OrderbookSearcher
from core.price_oracle import PriceOracle
from core.trade_container import TradeContainer
from core.trade_executor import TradeExecutor
from core.trading_config import TradingConfig
from core.trading_strategy import StrategyChoice, TradeStrategy
from loguru import logger


class MarketStatusObserverMixin(IMarketStatusObserverMixin):
    def __init__(self):
        self.containers: dict[StrategyChoice, TradeContainer] = {}

    async def on_market_status_changed(self, strategy_choice: StrategyChoice, should_trade: bool):
        if should_trade:
            if strategy_choice not in self.containers:
                config = TradeStrategy.get_config(self.config.symbol, self.config.badget, strategy_choice)
                container = TradeContainer(config, self.price_oracle, self.trade_executor)
                self.containers[strategy_choice] = container
                await container.start(self.notifier)
                logger.info(f"Started container for {strategy_choice}")
            await self.containers[strategy_choice].notify_market_status_changed(should_trade)
        else:
            if strategy_choice in self.containers:
                await self.containers[strategy_choice].notify_market_status_changed(should_trade)
                await self.containers[strategy_choice].stop()
                logger.info(f"Stopped container for {strategy_choice}")
                del self.containers[strategy_choice]


class TradingManager(MarketStatusObserverMixin):
    def __init__(self, config: TradingConfig, price_oracle: PriceOracle, trade_executor: TradeExecutor, notifier: Notifier):
        super().__init__()
        self.config = config
        self.price_oracle = price_oracle
        self.trade_executor = trade_executor
        self.notifier = notifier

    async def start_search(self, searcher: OrderbookSearcher):
        try:
            searcher.register_observer(self)
            await asyncio.gather(
                self.notifier.start(),
                searcher.start(self.config.delta),
                self.price_oracle.start(self.config.symbol)
            )
        except Exception as e:
            logger.error(f"Error in start_search: {e}")
        finally:
            await self.stop_all()

    async def stop_all(self):
        for container in self.containers.values():
            await container.stop()
        self.containers.clear()

    def get_status(self):
        return {
            "active_strategies": [strategy.value for strategy in self.containers.keys()],
            "container_statuses": {strategy: container.get_status() for strategy, container in self.containers.items()}
        }
