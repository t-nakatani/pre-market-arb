from typing import Any

from client.i_client import IExchangeClient
from core.types import Exchange
from loguru import logger


class Notifier:
    def __init__(self, trading_manager: 'TradingManager', bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.trading_manager = trading_manager
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client

    async def listen_bybit_limit_order(self):
        logger.info('start listening bybit limit order')
        while True:
            orders = await self.bybit_client.watch_orders()
            for order in orders:
                logger.debug(f'{order["id"]} {order["status"]} {order["side"]}')
                if order['status'] == 'filled':
                    logger.info(f'{order["id"]} filled in bybit')
                    self._notify_order_filled(Exchange.BYBIT, order)

    async def listen_hyperliquid_limit_order(self):
        logger.info('start listening hyperliquid limit order')
        while True:
            orders = await self.hyperliquid_client.watch_orders()
            for order in orders:
                logger.debug(f'{order["id"]} {order["status"]} {order["side"]}')
                if order['status'] == 'filled':
                    logger.info(f'{order["id"]} filled in hyperliquid')
                    self._notify_order_filled(Exchange.HYPERLIQUID, order)

    def _notify_order_filled(self, eaten_exchange: Exchange, order: dict[str, Any]):
        another_exchange = Exchange.HYPERLIQUID if eaten_exchange == Exchange.BYBIT else Exchange.BYBIT
        self.trading_manager.settle_another_side(another_exchange, order['side'], order['amount'], order['price'])
