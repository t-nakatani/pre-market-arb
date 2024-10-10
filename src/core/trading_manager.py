import asyncio

from core.notifier import Notifier
from core.price_oracle import PriceOracle
from core.trade_executor import TradeExecutor
from core.types import Exchange, Side


class TradingConfig:
    def __init__(self, symbol: str, badget: float, delta: float = 0.05):
        self.symbol = symbol
        self.badget = badget
        self.delta = delta


class TradingManager:
    def __init__(self, config: TradingConfig, executor: TradeExecutor, price_oracle: PriceOracle):
        self.config = config
        self.executor = executor
        self.price_oracle = price_oracle

    def attach_notifier(self, notifier: Notifier):
        self.notifier = notifier

    async def _place_market_order(self, exchange: Exchange, side: Side, amount: float):
        pass

    def _get_amount(self):
        # TODO: refine
        # return self.config.badget / mid_price
        return 8
    
    async def _place_dual_limit_orders(self):
        await asyncio.sleep(20)
        while True:
            bybit_mid_price, hyperliquid_mid_price = await asyncio.gather(
                self.price_oracle.get_bybit_mid_price(self.config.symbol),
                self.price_oracle.get_hyperliquid_mid_price(self.config.symbol)
            )
            amount = self._get_amount()
            bybit_lower_price = bybit_mid_price * (1 - self.config.delta)
            bybit_higher_price = bybit_mid_price * (1 + self.config.delta)
            hyperliquid_lower_price = hyperliquid_mid_price * (1 - self.config.delta)
            hyperliquid_higher_price = hyperliquid_mid_price * (1 + self.config.delta)
            await self.executor.cancel_all_orders(self.config.symbol)
            await self.executor.place_dual_limit_orders(self.config.symbol, amount, (bybit_lower_price, bybit_higher_price), (hyperliquid_lower_price, hyperliquid_higher_price))

    async def update_dual_limit_orders(self):
        pass

    async def run(self):
        try:
            tasks = [
                self._place_dual_limit_orders(),
                self.price_oracle.watch_bybit_mid_prices(self.config.symbol),
                self.price_oracle.watch_hyperliquid_mid_prices(self.config.symbol),
                self.notifier.listen_bybit_limit_order(),
                self.notifier.listen_hyperliquid_limit_order()
            ]
            await asyncio.gather(*tasks)
        finally:
            await self.executor.close()

    async def settle_another_side(self, exchange: Exchange, side: str, amount: float, price: float):
        if price > 0:  # 将来的にmarket_orderとopen_positionのcloseに分岐
            return await self.executor._place_market_order(exchange, side, amount)

