import asyncio

from client.i_client import IExchangeClient
from core.types import Exchange, OrderType, Side
from loguru import logger


class TradeExecutor:
    def __init__(self, bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client

    async def _place_limit_order(self, exchange: Exchange, symbol: str, side: str, amount: float, price: float):
        # TODO
        client = self.bybit_client if exchange == Exchange.BYBIT else self.hyperliquid_client
        return client.place_order(symbol, 'limit', side, amount, price)

    async def place_dual_limit_orders(self, symbol: str, amount: float, bybit_prices: (float, float), hyperliquid_prices: (float, float)):
        bybit_lower_price, bybit_higher_price = bybit_prices
        hyperliquid_lower_price, hyperliquid_higher_price = hyperliquid_prices
        assert bybit_lower_price < bybit_higher_price
        assert hyperliquid_lower_price < hyperliquid_higher_price

        results = await asyncio.gather(
            self.bybit_client.place_order(symbol, OrderType.LIMIT, Side.SELL, amount, bybit_higher_price),
            self.bybit_client.place_order(symbol, OrderType.LIMIT, Side.BUY, amount, bybit_lower_price),
            self.hyperliquid_client.place_order(symbol, OrderType.LIMIT, Side.SELL, amount, hyperliquid_higher_price),
            self.hyperliquid_client.place_order(symbol, OrderType.LIMIT, Side.BUY, amount, hyperliquid_lower_price)
        )
        logger.debug('placed dual limit orders')
        return results

    async def place_market_order(self, exchange: Exchange, symbol: str, side: str, amount: float):
        # TODO
        client = self.bybit_client if exchange == Exchange.BYBIT else self.hyperliquid_client
        return client.place_market_order(symbol, side, amount)

    async def cancel_all_orders(self, symbol: str, bybit_order_ids: list[str], hyperliquid_order_ids: list[str]):
        await asyncio.gather(
            self.bybit_client.cancel_all_orders(symbol, bybit_order_ids),
            self.hyperliquid_client.cancel_all_orders(symbol, hyperliquid_order_ids)
        )

    async def close(self):
        await self.bybit_client.close()
        await self.hyperliquid_client.close()