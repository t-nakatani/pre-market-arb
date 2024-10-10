import asyncio

from core.notifier import Notifier
from core.price_oracle import PriceOracle
from core.trade_executor import TradeExecutor
from core.types import Exchange, Side


class TradingConfig:
    def __init__(self, symbol: str, badget: float):
        self.symbol = symbol
        self.badget = badget


class TradingManager:
    def __init__(self, config: TradingConfig, executor: TradeExecutor, price_oracle: PriceOracle):
        self.config = config
        self.executor = executor
        self.price_oracle = price_oracle

    def attach_notifier(self, notifier: Notifier):
        self.notifier = notifier

    async def _place_market_order(self, exchange: Exchange, side: Side, amount: float):
        pass

    async def _get_amount(self, exchange: Exchange, side: Side):
        # TODO: refine
        mid_price = await self.price_oracle.get_mid_prices(self.config.symbol)
        # return self.config.badget / mid_price
        return 1
    
    async def _place_dual_limit_orders(self, exchange: Exchange, side: Side):
        bybit_mid_price, hyperliquid_mid_price = await self.price_oracle.get_mid_prices(self.symbol)
        amount = self._get_amount(exchange, side)
        print(bybit_mid_price, hyperliquid_mid_price, amount)


    async def run(self):
        try:
            amount = await self._get_amount(Exchange.BYBIT, Side.BUY)
            tasks = [
                self.executor.place_dual_limit_orders(self.config.symbol, amount, (1, 2)),
                self.notifier.listen_bybit_limit_order(),
                self.notifier.listen_hyperliquid_limit_order()
            ]
            await asyncio.gather(*tasks)
        finally:
            await self.executor.close()

    async def settle_another_side(self, exchange: Exchange, side: str, amount: float, price: float):
        if price > 0:  # 将来的にmarket_orderとopen_positionのcloseに分岐
            return await self.executor._place_market_order(exchange, side, amount)

