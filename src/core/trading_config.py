from dataclasses import dataclass

from core.types import LimitInfo


@dataclass
class TradingConfig:
    symbol: str
    badget: float
    delta: float = 0.05
    limit_info: LimitInfo = None
