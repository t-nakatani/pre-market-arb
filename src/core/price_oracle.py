import asyncio
from typing import Optional

from client.i_client import IExchangeClient
from loguru import logger


class BestPrices:
    def __init__(self, best_bid: float, best_ask: float):
        if best_bid > best_ask:
            raise ValueError("best_bid must be less than best_ask")
        self.bid = best_bid
        self.ask = best_ask


class PriceOracle:
    def __init__(self, bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client
        self._bybit_best_price: Optional[BestPrices] = None
        self._hyperliquid_best_price: Optional[BestPrices] = None
        self._lock = asyncio.Lock()

    @property
    async def bybit_best_prices(self) -> Optional[BestPrices]:
        async with self._lock:
            return self._bybit_best_price

    @property
    async def hyperliquid_best_prices(self) -> Optional[BestPrices]:
        async with self._lock:
            return self._hyperliquid_best_price

    async def _watch_bybit_best_prices(self, symbol: str):
        while True:
            bybit_order_book = await self.bybit_client.watch_orderbook(symbol)
            bybit_asks = bybit_order_book['asks']
            bybit_bids = bybit_order_book['bids']
            self._bybit_best_price = BestPrices(
                best_bid=bybit_bids[0][0],
                best_ask=bybit_asks[0][0]
            )

    async def _watch_hyperliquid_best_prices(self, symbol: str):
        while True:
            hyperliquid_order_book = await self.hyperliquid_client.watch_orderbook(symbol)
            hyperliquid_asks = hyperliquid_order_book['asks']
            hyperliquid_bids = hyperliquid_order_book['bids']
            self._hyperliquid_best_price = BestPrices(
                best_bid=hyperliquid_bids[0][0],
                best_ask=hyperliquid_asks[0][0]
            )

    async def start(self, symbol: str):
        try:
            await asyncio.gather(
                self._watch_bybit_best_prices(symbol),
                self._watch_hyperliquid_best_prices(symbol)
            )
        finally:
            pass
