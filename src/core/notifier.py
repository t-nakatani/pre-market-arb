import asyncio
from typing import Any

from client.i_client import IExchangeClient
from core.observer_pattern.i_observer_mixin import ISettleObserverMixin
from core.types import Exchange
from loguru import logger


class Notifier:
    def __init__(self, bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client
        self.is_running = False
        self.tasks = []
        self.observers: dict[ISettleObserverMixin, str] = {}

    def register_observer(self, observer: ISettleObserverMixin):
        self.observers[observer] = None

    def update_topic(self, observer: ISettleObserverMixin, topic: str):
        self.observers[observer] = topic

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
                logger.info(f'{order["id"]} {order["status"]} {order["side"]}')
                if order['status'] == 'closed':
                    logger.info(f'{order["id"]} filled in bybit')
                    for observer, order_id in self.observers.items():
                        logger.debug(f"order_id: {order_id}, order['id']: {order['id']}")
                        if order['id'] == order_id:
                            try:
                                await observer.on_order_filled(Exchange.BYBIT, order)
                            except Exception as e:
                                logger.error(f"Error in observer.on_order_filled: {e}")

    async def listen_hyperliquid_limit_order(self):
        logger.info('start listening hyperliquid limit order')
        while self.is_running:
            orders = await self.hyperliquid_client.watch_orders()
            for order in orders:
                logger.debug(f'{order["id"]} {order["status"]} {order["side"]}')
                if order['status'] == 'closed':
                    logger.info(f'{order["id"]} filled in hyperliquid')
                    for observer, order_id in self.observers.items():
                        logger.debug(f"order_id: {order_id}, order['id']: {order['id']}")
                        if order['id'] == order_id:
                            try:
                                await observer.on_order_filled(Exchange.HYPERLIQUID, order)
                            except Exception as e:
                                logger.error(f"Error in observer.on_order_filled: {e}")
