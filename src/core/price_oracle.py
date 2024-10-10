from client.i_client import IExchangeClient


class PriceOracle:
    def __init__(self, bybit_client: IExchangeClient, hyperliquid_client: IExchangeClient):
        self.bybit_client = bybit_client
        self.hyperliquid_client = hyperliquid_client
    
    async def get_mid_prices(self, symbol: str) -> (float, float):
        bybit_order_book = await self.bybit_client.get_orderbook(symbol)
        # hyperliquid_order_book = await self.hyperliquid_client.get_orderbook(symbol)

        bybit_asks = bybit_order_book['asks']
        bybit_bids = bybit_order_book['bids']
        # hyperliquid_asks = hyperliquid_order_book['asks']
        # hyperliquid_bids = hyperliquid_order_book['bids']

        bybit_mid_price = (bybit_asks[0][0] + bybit_bids[0][0]) / 2
        # hyperliquid_mid_price = (hyperliquid_asks[0][0] + hyperliquid_bids[0][0]) / 2

        return bybit_mid_price, 1.5
