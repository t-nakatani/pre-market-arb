from core.observer_mixin import MarketStatusObserverMixin
from core.orderbook_searcher import OrderbookSearcher
from core.price_oracle import PriceOracle
from core.trade_container import TradeContainer
from core.trade_executor import TradeExecutor
from core.tradind_config import TradingConfig
from core.trading_strategy import StrategyChoice
from core.types import Exchange, Side


class Orders:
    def __init__(self):
        self.bybit_order_ids: list[str] = []
        self.hyperliquid_order_ids: list[str] = []

    def pop_bybit_order_ids(self) -> list[str]:
        order_ids = self.bybit_order_ids
        self.bybit_order_ids = []
        return order_ids

    def pop_hyperliquid_order_ids(self) -> list[str]:
        order_ids = self.hyperliquid_order_ids
        self.hyperliquid_order_ids = []
        return order_ids


class TradingManager(MarketStatusObserverMixin):
    def __init__(self, config: TradingConfig, price_oracle: PriceOracle, trade_executor: TradeExecutor):
        self.config = config
        self.price_oracle = price_oracle
        self.trade_executor = trade_executor
        self.containers: dict[StrategyChoice, TradeContainer] = {}

    async def start_search(self, searcher: OrderbookSearcher):
        searcher.register_observer(self)
        await searcher.start(self.config.delta)

    async def on_market_status_changed(self, strategy_choice: StrategyChoice, should_trade: bool):
        if should_trade:
            if strategy_choice not in self.containers:
                container = TradeContainer(self.config, self.price_oracle, self.trade_executor)
                self.containers[strategy_choice] = container
                await container.start()
            await self.containers[strategy_choice].notify_market_status_changed(should_trade)
        else:
            if strategy_choice in self.containers:
                await self.containers[strategy_choice].notify_market_status_changed(should_trade)
                await self.containers[strategy_choice].stop()
                del self.containers[strategy_choice]

    async def settle_another_side(self, exchange: Exchange, side: Side, amount: float, price: float):
        # 反対側の注文を決済するロジックを実装
        opposite_side = Side.SELL if side == Side.BUY else Side.BUY
        for container in self.containers.values():
            if container.strategy_choice.value.startswith(f"limit_{side.value}_{exchange.value}"):
                await container.settle_opposite_order(opposite_side, amount, price)
                break

    async def stop_all(self):
        for container in self.containers.values():
            await container.stop()
        self.containers.clear()

    def get_status(self):
        return {
            "active_strategies": [strategy.value for strategy in self.containers.keys()],
            "container_statuses": {strategy: container.get_status() for strategy, container in self.containers.items()}
        }
