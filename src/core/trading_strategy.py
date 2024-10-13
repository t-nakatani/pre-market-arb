from enum import Enum

from core.types import Exchange


class StrategyChoice(Enum):
    LIMIT_SELL_BYBIT_MARKET_BUY_HYLIQ = 'limit-sell-bybit-market-buy-hyliq'
    LIMIT_SELL_HYLIQ_MARKET_BUY_BYBIT = 'limit-sell-hyliq-market-buy-bybit'
    LIMIT_BUY_BYBIT_MARKET_SELL_HYLIQ = 'limit-buy-bybit-market-sell-hyliq'
    LIMIT_BUY_HYLIQ_MARKET_SELL_BYBIT = 'limit-buy-hyliq-market-sell-bybit'

class TradeStrategy:
    @staticmethod
    def judge(best_prices: dict[Exchange, dict[str, float]], threshold: float) -> dict[StrategyChoice, bool]:
        result = {}
        bybit_ask = best_prices[Exchange.BYBIT]['ask']
        bybit_bid = best_prices[Exchange.BYBIT]['bid']
        hyperliquid_ask = best_prices[Exchange.HYPERLIQUID]['ask']
        hyperliquid_bid = best_prices[Exchange.HYPERLIQUID]['bid']

        result[StrategyChoice.LIMIT_SELL_BYBIT_MARKET_BUY_HYLIQ] = (hyperliquid_ask - bybit_ask) / bybit_ask > threshold
        result[StrategyChoice.LIMIT_SELL_HYLIQ_MARKET_BUY_BYBIT] = (hyperliquid_ask - bybit_ask) / bybit_ask > threshold
        result[StrategyChoice.LIMIT_BUY_BYBIT_MARKET_SELL_HYLIQ] = (hyperliquid_bid - bybit_bid) / bybit_bid > threshold
        result[StrategyChoice.LIMIT_BUY_HYLIQ_MARKET_SELL_BYBIT] = (bybit_bid - hyperliquid_bid) / hyperliquid_bid > threshold
        return result
