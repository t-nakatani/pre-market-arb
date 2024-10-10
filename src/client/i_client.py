from abc import ABC, abstractmethod
from typing import Any

from core.types import Side


class IExchangeClient(ABC):

    @abstractmethod
    def _as_pair(self, symbol: str) -> str:
        pass

    @abstractmethod
    async def get_orderbook(self, symbol: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def place_order(self, symbol: str, order_type: str, side: Side, amount: float, price: float = None):
        pass

    @abstractmethod
    async def watch_orders(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def close(self):
        pass
