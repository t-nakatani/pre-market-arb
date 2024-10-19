# TODO: oracleを使ってリファクタリングする
import asyncio

import ccxt.pro as ccxt
from client.bybit_client import BybitClient
from client.hyperliquid_client import HyperliquidClient
from core.observer_pattern.i_observer_mixin import IMarketStatusObserverMixin
from core.trading_strategy import StrategyChoice, TradeStrategy
from core.types import Exchange
from loguru import logger


class OrderbookSearcher:
    def __init__(self, symbol: str, ccxt_bybit_client: ccxt.Exchange, ccxt_hyperliquid_client: ccxt.Exchange):
        self.observers = []
        self.symbol = symbol
        self.bybit_client = BybitClient(ccxt_bybit_client)
        self.hyperliquid_client = HyperliquidClient(ccxt_hyperliquid_client)
        self.bybit_queue = asyncio.Queue()
        self.hyperliquid_queue = asyncio.Queue()

    def register_observer(self, observer: IMarketStatusObserverMixin):
        self.observers.append(observer)

    async def notify_market_status_changed(self, strategy_choice: StrategyChoice, activate: bool):
        for observer in self.observers:
            await observer.on_market_status_changed(strategy_choice, activate)

    async def _watch_best_prices(self, client: ccxt.Exchange, queue: asyncio.Queue):
        while True: 
            order_book = await client.watch_orderbook(self.symbol)
            best_bid = order_book['bids'][0]
            best_ask = order_book['asks'][0]
            await queue.put((str(client), best_bid, best_ask))
            await asyncio.sleep(0.2)

    async def _compare_best_prices(self, trade_threshold: float):
        async def _get_best_prices():
            bybit_data = await self.bybit_queue.get()
            hyperliquid_data = await self.hyperliquid_queue.get()
            bybit_bid, bybit_ask = bybit_data[1][0], bybit_data[2][0]
            hyperliquid_bid, hyperliquid_ask = hyperliquid_data[1][0], hyperliquid_data[2][0]

            best_prices = {
                Exchange.BYBIT: {"bid": bybit_bid, "ask": bybit_ask},
                Exchange.HYPERLIQUID: {"bid": hyperliquid_bid, "ask": hyperliquid_ask}
            }
            return best_prices

        while True:
            best_prices = await _get_best_prices()
            search_results = TradeStrategy.judge(best_prices, threshold=trade_threshold)
            for strategy_choice, should_trade in search_results.items():
                await self.notify_market_status_changed(strategy_choice, should_trade)
            await asyncio.sleep(0.1)

    async def start(self, trade_threshold: float):
        logger.info("Starting OrderbookMonitor")
        try:
            await asyncio.gather(
                self._watch_best_prices(self.bybit_client, self.bybit_queue),
                self._watch_best_prices(self.hyperliquid_client, self.hyperliquid_queue),
                self._compare_best_prices(trade_threshold)
            )
        finally:
            await self.bybit_client.close()
            await self.hyperliquid_client.close()
