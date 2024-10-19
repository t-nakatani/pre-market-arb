import asyncio
from typing import Optional

from client.i_client import IExchangeClient
from core.exceptions import OrderClosedException
from core.types import Exchange, OrderType, Side
from loguru import logger


class TradeExecutor:
    def __init__(self, bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client

    async def _place_new_limit_order(self, exchange: Exchange, symbol: str, side: str, amount: float, price: float):
        # TODO
        client = self.bybit_client if exchange == Exchange.BYBIT else self.hyperliquid_client
        return await client.place_order(symbol, OrderType.LIMIT, side, amount, price)

    async def _edit_limit_order(self, exchange: Exchange, order_id: str, symbol: str, side: str, amount: float, price: float):
        client = self.bybit_client if exchange == Exchange.BYBIT else self.hyperliquid_client
        return await client.edit_order(order_id, symbol, OrderType.LIMIT, side, amount, price)

    async def place_market_order(self, exchange: Exchange, symbol: str, side: str, amount: float):
        client = self.bybit_client if exchange == Exchange.BYBIT else self.hyperliquid_client
        return await client.place_order(symbol, OrderType.MARKET, side, amount)

    async def cancel_order(self, exchange: Exchange, order_id: str, symbol: str):
        client = self.bybit_client if exchange == Exchange.BYBIT else self.hyperliquid_client
        return await client.cancel_order(order_id, symbol)

    async def cancel_all_orders(self, symbol: str, bybit_order_ids: list[str], hyperliquid_order_ids: list[str]):
        await asyncio.gather(
            self.bybit_client.cancel_all_orders(symbol, bybit_order_ids),
            self.hyperliquid_client.cancel_all_orders(symbol, hyperliquid_order_ids)
        )

    async def place_limit_order(self, exchange: Exchange, order_id: Optional[str], symbol: str, side: Side, amount: float, price: float) -> str:
        if not order_id:
            order_id = await self._place_new_limit_order(exchange, symbol, side.value, amount, price)
            logger.info(f"Placed limit order: {symbol}, {side}, {amount}, {price}, {order_id}")
        else:
            order_id = await self._edit_limit_order(exchange, order_id, symbol, side.value, amount, price)
            logger.info(f"Edited limit order: {symbol}, {side}, {amount}, {price}, {order_id}")
        return order_id
