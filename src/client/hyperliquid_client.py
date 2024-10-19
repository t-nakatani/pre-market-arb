from functools import wraps
from typing import Any

from client.hyperliquid_decorator import handle_order_errors
from client.i_client import IExchangeClient
from core.exceptions import OrderClosedException
from core.types import OrderType, Side
from loguru import logger


def with_user_params(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> list[dict[str, Any]]:
        user_param = {'user': '0x81263f67a6354e58C54f485963ebcb6058422940'}
        if 'params' in kwargs:
            kwargs['params'].update(user_param)
        else:
            kwargs['params'] = user_param
        return await func(self, *args, **kwargs)
    return wrapper

class HyperliquidClient(IExchangeClient):
    def __init__(self, ccxt_client):
        self.exchange = ccxt_client

    def __str__(self):
        return "hyperliquid"

    def _as_pair(self, symbol: str) -> str:
        return f'{symbol}/USDC:USDC'

    async def fetch_precision(self, symbol: str) -> tuple[float, float]:
        await self.exchange.load_markets()
        market = self.exchange.market(self._as_pair(symbol))
        assert type(market['precision']['price']) is int, "price precision is not int"
        price_tick = 10 ** - (market['precision']['price'] - 1)
        amount_tick = 10 ** - market['precision']['amount']
        return price_tick, amount_tick

    async def watch_orderbook(self, symbol: str) -> dict[str, Any]:
        return await self.exchange.watch_order_book(self._as_pair(symbol))

    @handle_order_errors
    async def place_order(self, symbol: str, order_type: OrderType, side: Side, amount: float, price: float):
        reciept = await self.exchange.create_order(symbol=self._as_pair(symbol), type=order_type.value, side=side.value, amount=amount, price=price)
        return reciept['id']

    @handle_order_errors
    async def edit_order(self, order_id: str, symbol: str, order_type: OrderType, side: Side, amount: float, price: float):
        try:
            reciept = await self.exchange.edit_order(order_id, symbol=self._as_pair(symbol), type=order_type.value, side=side.value, amount=amount, price=price)
            return reciept['id']
        except Exception as e:
            logger.error(f"Failed to edit order: {e}")
            closed_orders = await self.exchange.fetch_closed_order(order_id, self._as_pair(symbol))
            if closed_orders:
                raise OrderClosedException
            return None

    @with_user_params
    async def watch_orders(self, **kwargs) -> list[dict[str, Any]]:
        return await self.exchange.watch_orders(**kwargs)

    async def cancel_order(self, order_id: str, symbol: str):
        try:
            return await self.exchange.cancel_order(order_id, self._as_pair(symbol))
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return None

    async def cancel_all_orders(self, symbol: str, order_ids: list[str]):
        if not order_ids:
            return
        return await self.exchange.cancel_orders(ids=order_ids, symbol=self._as_pair(symbol))

    async def close(self):
        await self.exchange.close()
