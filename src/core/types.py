from dataclasses import dataclass
from enum import Enum


class Exchange(Enum):
    BYBIT = 'bybit'
    HYPERLIQUID = 'hyperliquid'


class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'


class OrderType(Enum):
    LIMIT = 'limit'
    MARKET = 'market'


@dataclass
class LimitInfo:
    exchange: Exchange
    side: Side
