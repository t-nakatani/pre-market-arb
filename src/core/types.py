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

class BestPrices:
    def __init__(self, best_bid: float, best_ask: float):
        if best_bid > best_ask:
            raise ValueError("best_bid must be less than best_ask")
        self.bid = best_bid
        self.ask = best_ask
