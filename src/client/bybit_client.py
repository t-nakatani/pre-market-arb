from typing import Any

from client.i_client import IExchangeClient
from core.types import OrderType, Side
from loguru import logger


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

    async def edit_order(self, order_id: str, symbol: str, order_type: OrderType, side: Side, amount: float, price: float):
        try:
            return await self.exchange.edit_order(order_id, self._as_pair(symbol), order_type.value, side.value, str(amount), price)
        except Exception as e:
            logger.error(f"Failed to edit order: {e}")
            return None

    async def watch_orders(self) -> list[dict[str, Any]]:
        return await self.exchange.watch_orders()

    async def cancel_order(self, order_id: str, symbol: str):
        try:
            return await self.exchange.cancel_order(order_id, self._as_pair(symbol))
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return None

    async def cancel_all_orders(self, symbol: str, order_ids: list[str]):
        if not order_ids:
            return
        return await self.exchange.cancel_all_orders(self._as_pair(symbol))

    async def close(self):
        await self.exchange.close()
