import asyncio
from typing import Optional

from core.exceptions import OrderClosedException
from core.notifier import Notifier
from core.price_oracle import PriceOracle
from core.trade_executor import TradeExecutor
from core.trading_config import TradingConfig
from core.types import Exchange, Side
from loguru import logger


class TradeContainer:
    def __init__(self, trade_config: TradingConfig, price_oracle: PriceOracle, trade_executor: TradeExecutor):
        self.is_running: bool = False
        self.task: Optional[asyncio.Task] = None
        self.trade_config: TradingConfig = trade_config
        self.price_oracle: PriceOracle = price_oracle
        self.trade_executor: TradeExecutor = trade_executor
        self.notifier: Optional[Notifier] = None
        logger.debug(f"TradeContainer initialized: {self.trade_config.symbol}")

    def get_status(self) -> dict:
        """取引の状態を取得します。"""
        return {
            "is_running": self.is_running,
            "trade_config": self.trade_config,
        }

    def get_amount(self) -> float:
        """取引量を取得します。"""
        return 8.0

    def attach_notifier(self, notifier: Notifier) -> None:
        """ノーティファイアをアタッチします。"""
        notifier.register_observer(self)
        self.notifier = notifier

    async def start(self, notifier: Notifier) -> None:
        """取引を開始します。"""
        if not self.is_running:
            self.is_running = True
            self.attach_notifier(notifier)
            self.task = asyncio.create_task(self._sticky_limit_order())
            logger.debug(f"TradeContainer started: {self.trade_config.symbol}")

    async def stop(self) -> None:
        """取引を停止します。"""
        if self.is_running:
            self.is_running = False
            if self.task:
                await self.task
            logger.debug(f"TradeContainer stopped: {self.trade_config.symbol}")

    def _update_order_id(self, order_id: str) -> None:
        """注文IDを更新します。"""
        if self.notifier:
            self.notifier.update_topic(self, topic=order_id)

    async def _sticky_limit_order(self) -> None:
        """スティッキーリミットオーダーを実行します。"""
        try:
            order_id = None
            limit_price = None
            while self.is_running:
                best_prices = await self._get_best_prices()
                if not best_prices:
                    logger.info(f"No best prices for {self.trade_config.symbol}")
                    await asyncio.sleep(1)
                    continue

                new_limit_price = self._determine_limit_price(best_prices)
                if new_limit_price == limit_price:
                    await asyncio.sleep(0.1)
                    continue

                limit_price = new_limit_price
                amount = self.get_amount()
                order_id = await self._place_or_edit_order(order_id, limit_price, amount)
                self._update_order_id(order_id)
                await asyncio.sleep(0.2)
                logger.info(f"Updated order id: {order_id}")

            await self.trade_executor.cancel_order(self.trade_config.limit_info.exchange, self.trade_config.symbol, self.trade_config.limit_info.side)
            logger.info(f"Stopped _sticky_limit_order: {self.trade_config.symbol}")
        except Exception as e:
            logger.error(f"Error in _sticky_limit_order: {e}")

    async def _get_best_prices(self) -> Optional:
        """最良価格を取得します。"""
        if self.trade_config.limit_info.exchange == Exchange.BYBIT:
            return await self.price_oracle.get_bybit_best_prices()
        return await self.price_oracle.get_hyperliquid_best_prices()

    def _determine_limit_price(self, best_prices) -> float:
        """リミット価格を決定します。"""
        return best_prices.bid if self.trade_config.limit_info.side == Side.BUY else best_prices.ask

    async def _place_limit_order(self, order_id, limit_price, amount):
        """注文を配置または編集します。"""
        try:
            order_id = await self.trade_executor.place_limit_order(
                exchange=self.trade_config.limit_info.exchange,
                order_id=order_id,
                symbol=self.trade_config.symbol,
                side=self.trade_config.limit_info.side,
                amount=amount,
                price=limit_price
            )
        except OrderClosedException:
            order_id = None
            await self._settle_another_side(
                exchange=self.trade_config.limit_info.exchange,
                side=self.trade_config.limit_info.side,
                amount=amount,
                price=limit_price
            )
        return order_id

    async def notify_market_status_changed(self, should_trade: bool) -> None:
        """市場の状態が変化したときに通知します。"""
        pass

    async def on_order_filled(self, exchange: Exchange, order: dict) -> None:
        """注文が約定されたときの処理を行います。"""
        logger.info(f"Order filled: {order['id']}")
        amount = self.get_amount()
        another_side = Side.BUY if order['side'] == Side.SELL.value else Side.SELL
        another_exchange = Exchange.BYBIT if exchange == Exchange.HYPERLIQUID else Exchange.HYPERLIQUID
        await self._settle_another_side(another_exchange, another_side, amount)

    async def _settle_another_side(self, exchange: Exchange, side: Side, amount: float) -> None:
        """反対側の注文を決済します。"""
        logger.info(f"Placing market order: {self.trade_config.symbol}, {side.value}, {amount}")
        order_id = await self.trade_executor.place_market_order(exchange, self.trade_config.symbol, side, amount)
        logger.info(f"Settled opposite order for {self.trade_config.symbol}: {side.value} {amount}, {order_id}")
