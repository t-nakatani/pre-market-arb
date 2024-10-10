from functools import wraps
from typing import Any

from client.i_client import IExchangeClient
from core.types import Side


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
    
    def _as_pair(self, symbol: str) -> str:
        return f'{symbol}/USDC:USDC'

    async def get_orderbook(self, symbol: str) -> dict[str, Any]:
        return await self.exchange.fetch_order_book(self._as_pair(symbol))

    async def place_order(self, symbol: str, order_type: str, side: Side, amount: float, price: float = None):
        return await self.exchange.create_order(self._as_pair(symbol), order_type, side.value, amount, price)

    @with_user_params
    async def watch_orders(self, **kwargs) -> list[dict[str, Any]]:
        return await self.exchange.watch_orders(**kwargs)

    async def close(self):
        await self.exchange.close()
