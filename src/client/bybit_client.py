from typing import Any

from core.types import OrderType, Side

from client.i_client import IExchangeClient


class BybitClient(IExchangeClient):
    def __init__(self, ccxt_client):
        self.exchange = ccxt_client

    async def get_orderbook(self, symbol: str) -> dict[str, Any]:
        return await self.exchange.fetch_order_book(symbol)

    async def place_order(self, symbol: str, order_type: OrderType, side: Side, amount: float, price: float = None):
        return await self.exchange.create_order(symbol, order_type.value, side.value, amount, price)

    async def watch_orders(self) -> list[dict[str, Any]]:
        return await self.exchange.watch_orders()

    async def close(self):
        await self.exchange.close()
