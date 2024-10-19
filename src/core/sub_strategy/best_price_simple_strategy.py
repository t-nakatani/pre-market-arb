from core.types import BestPrices, Side

from .i_sub_strategy import ISubStrategy


class BestPriceSimpleStrategy(ISubStrategy):
    def determine_limit_price(self, best_prices: BestPrices, side: Side, price_precision: float) -> float:
        """リミット価格を決定します。"""
        return best_prices.bid if side == Side.BUY else best_prices.ask

