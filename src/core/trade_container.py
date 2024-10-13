import asyncio

from core.notifier import Notifier
from core.price_oracle import PriceOracle
from core.trade_executor import TradeExecutor
from core.tradind_config import TradingConfig
from core.types import Exchange
from loguru import logger


class TradeContainer:
    def __init__(self, trade_config: TradingConfig, price_oracle: PriceOracle, trade_executor: TradeExecutor):
        self.trade_config = trade_config
        self.is_running = False
        self.task = None
        self.price_oracle = price_oracle
        self.trade_executor = trade_executor

    async def start(self):
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self._trading_loop())

    async def stop(self):
        if self.is_running:
            self.is_running = False
            if self.task:
                await self.task

    async def attach_notifier(self, notifier: Notifier):
        notifier.register_observer(self)

    async def _trading_loop(self):
        while self.is_running:
            await self._execute_trade()
            await asyncio.sleep(1)  # 1秒ごとに取引を確認

    async def _execute_trade(self):
        # ここで実際の非同期取引ロジックを実装します
        # 例: await self.trading_manager.execute_strategy(self.strategy_choice)
        logger.info(f"executing_trade: {self.trade_config.symbol}")
        await asyncio.sleep(1)

    async def notify_market_status_changed(self, should_trade: bool):
        pass

    def get_status(self):
        return {
            "is_running": self.is_running,
            "trade_config": self.trade_config,
        }

    async def on_order_filled(self, exchange: Exchange, order: dict):
        await self.trade_executor.on_order_filled(exchange, order)

    # async def settle_opposite_order(self, side: Side, amount: float, price: float):
    #     # 反対側の注文を決済するロジックを実装
    #     exchange = Exchange.BYBIT if self.strategy_choice.value.endswith("_bybit") else Exchange.HYPERLIQUID
    #     await self.trade_executor.place_market_order(exchange, self.trade_config.symbol, side.value, amount)
    #     logger.info(f"Settled opposite order for {self.strategy_choice}: {side.value} {amount} @ {price}")
