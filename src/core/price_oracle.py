import asyncio
from typing import Optional

from client.i_client import IExchangeClient


class PriceOracle:
    _bybit_mid_price: float
    _hyperliquid_mid_price: float

    def __init__(self, bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client
        self._bybit_mid_price: Optional[float] = None
        self._hyperliquid_mid_price: Optional[float] = None
        self._lock = asyncio.Lock()

    async def watch_bybit_mid_prices(self, symbol: str):
        while True:
            bybit_order_book = await self.bybit_client.watch_orderbook(symbol)
            bybit_asks = bybit_order_book['asks']
            bybit_bids = bybit_order_book['bids']
            self._bybit_mid_price = (bybit_asks[0][0] + bybit_bids[0][0]) / 2

    async def watch_hyperliquid_mid_prices(self, symbol: str):
        while True:
            hyperliquid_order_book = await self.hyperliquid_client.watch_orderbook(symbol)
            hyperliquid_asks = hyperliquid_order_book['asks']
            hyperliquid_bids = hyperliquid_order_book['bids']
            self._hyperliquid_mid_price = (hyperliquid_asks[0][0] + hyperliquid_bids[0][0]) / 2

    async def get_bybit_mid_price(self, symbol: str) -> float:
        async with self._lock:
            return self._bybit_mid_price

    async def get_hyperliquid_mid_price(self, symbol: str) -> float:
        async with self._lock:
            return self._hyperliquid_mid_price
