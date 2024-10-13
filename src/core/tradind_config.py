class TradingConfig:
    def __init__(self, symbol: str, badget: float, delta: float = 0.05):
        self.symbol = symbol
        self.badget = badget
        self.delta = delta
