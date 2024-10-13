import asyncio
from typing import Any

from client.i_client import IExchangeClient
from core.observer_mixin import SettleObserverMixin
from core.types import Exchange
from loguru import logger


class Notifier:
    def __init__(self, bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client
        self.is_running = False
        self.tasks = []

    def register_observer(self, observer: SettleObserverMixin):
        self.observer = observer

    async def start(self):
        if not self.is_running:
            self.is_running = True
            self.tasks = [
                asyncio.create_task(self.listen_bybit_limit_order()),
                asyncio.create_task(self.listen_hyperliquid_limit_order())
            ]

    async def stop(self):
        if self.is_running:
            self.is_running = False
            for task in self.tasks:
                task.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks = []

    async def listen_bybit_limit_order(self):
        logger.info('start listening bybit limit order')
        while self.is_running:
            orders = await self.bybit_client.watch_orders()
            for order in orders:
                logger.debug(f'{order["id"]} {order["status"]} {order["side"]}')
                if order['status'] == 'closed':
                    logger.info(f'{order["id"]} filled in bybit')
                    await self.observer.on_order_filled(Exchange.BYBIT, order)

    async def listen_hyperliquid_limit_order(self):
        logger.info('start listening hyperliquid limit order')
        while self.is_running:
            orders = await self.hyperliquid_client.watch_orders()
            for order in orders:
                logger.debug(f'{order["id"]} {order["status"]} {order["side"]}')
                if order['status'] == 'closed':
                    logger.info(f'{order["id"]} filled in hyperliquid')
                    await self.observer.on_order_filled(Exchange.HYPERLIQUID, order)
