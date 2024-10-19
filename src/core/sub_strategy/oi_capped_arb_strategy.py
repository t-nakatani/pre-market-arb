from typing import Side

from .i_sub_strategy import ISubStrategy


class OiCappedArbStrategy(ISubStrategy):
    def determine_limit_price(self, best_prices) -> float:
        """リミット価格を決定します。"""
        return best_prices.bid if self.trade_config.limit_info.side == Side.BUY else best_prices.ask
