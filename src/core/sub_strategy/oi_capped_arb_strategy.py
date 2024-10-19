from core.types import BestPrices, Side

from .i_sub_strategy import ISubStrategy


class BestPriceSimpleStrategy(ISubStrategy):
    def determine_limit_price(self, best_prices: BestPrices, side: Side, price_precision: float) -> float:
        """リミット価格を決定します。"""
        current_ask_subex = best_prices.ask
        current_bid_subex = best_prices.bid
        
        if side == Side.SELL:
            return current_bid_subex + price_precision
        elif side == Side.BUY:
            return current_ask_subex - price_precision
        raise ValueError(f"Invalid side: {side}")
