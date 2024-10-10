from typing import Any

from client.i_client import IExchangeClient
from core.types import OrderType, Side


class BybitClient(IExchangeClient):
    def __init__(self, ccxt_client):
        self.exchange = ccxt_client

    def _as_pair(self, symbol: str) -> str:
        return f'{symbol}USDT'

    async def get_orderbook(self, symbol: str) -> dict[str, Any]:
        return await self.exchange.fetch_order_book(self._as_pair(symbol))

    async def place_order(self, symbol: str, order_type: OrderType, side: Side, amount: float, price: float = None):
        return await self.exchange.create_order(self._as_pair(symbol), order_type.value, side.value, str(amount), price)

    async def watch_orders(self) -> list[dict[str, Any]]:
        return await self.exchange.watch_orders()

    async def close(self):
        await self.exchange.close()
