import asyncio

from client.i_client import IExchangeClient

from core.types import Exchange, OrderType, Side


class TradeExecutor:
    def __init__(self, bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client

    async def _place_limit_order(self, exchange: Exchange, symbol: str, side: str, amount: float, price: float):
        # TODO
        client = self.bybit_client if exchange == Exchange.BYBIT else self.hyperliquid_client
        return client.place_order(symbol, 'limit', side, amount, price)

    async def place_dual_limit_orders(self, symbol: str, amount: float, prices: (float, float)):
        await asyncio.sleep(5)
        lower_price, higher_price = prices
        assert lower_price < higher_price

        # SELL higher price
        await self.bybit_client.place_order(symbol, OrderType.LIMIT, Side.SELL, amount, higher_price)
        # await self.hyperliquid_client.place_order(symbol, 'limit', Side.SELL, amount, higher_price)

        # BUY lower price
        await self.bybit_client.place_order(symbol, OrderType.LIMIT, Side.BUY, amount, lower_price)
        # await self.hyperliquid_client.place_order(symbol, 'limit', Side.BUY, amount, lower_price)
        print('placed dual limit orders')

    async def place_market_order(self, exchange: Exchange, symbol: str, side: str, amount: float):
        # TODO
        client = self.bybit_client if exchange == Exchange.BYBIT else self.hyperliquid_client
        return client.place_market_order(symbol, side, amount)

    async def close(self):
        await self.bybit_client.close()
        await self.hyperliquid_client.close()