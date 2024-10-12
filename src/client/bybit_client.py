from typing import Any

from client.i_client import IExchangeClient
from core.types import OrderType, Side


class BybitClient(IExchangeClient):
    def __init__(self, ccxt_client):
        self.exchange = ccxt_client

    def __str__(self):
        return "bybit"

    def _as_pair(self, symbol: str) -> str:
        return f'{symbol}USDT'

    async def watch_orderbook(self, symbol: str) -> dict[str, Any]:
        return await self.exchange.watch_order_book(self._as_pair(symbol))

    async def place_order(self, symbol: str, order_type: OrderType, side: Side, amount: float, price: float = None):
        reciept = await self.exchange.create_order(self._as_pair(symbol), order_type.value, side.value, str(amount), price)
        return reciept['info']['orderId']

    async def watch_orders(self) -> list[dict[str, Any]]:
        return await self.exchange.watch_orders()

    async def cancel_all_orders(self, symbol: str, order_ids: list[str]):
        if not order_ids:
            return
        return await self.exchange.cancel_all_orders(self._as_pair(symbol))

    async def close(self):
        await self.exchange.close()
