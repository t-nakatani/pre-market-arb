from abc import ABC, abstractmethod
from typing import Any

from core.types import OrderType, Side


class IExchangeClient(ABC):

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def _as_pair(self, symbol: str) -> str:
        pass

    @abstractmethod
    async def watch_orderbook(self, symbol: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def place_order(self, symbol: str, order_type: OrderType, side: Side, amount: float, price: float = None):
        pass

    @abstractmethod
    async def watch_orders(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def cancel_all_orders(self, symbol: str, order_ids: list[str]):
        pass

    @abstractmethod
    async def close(self):
        pass
