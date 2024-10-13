import asyncio
import os

import ccxt.pro as ccxt_pro
from client.bybit_client import BybitClient
from client.hyperliquid_client import HyperliquidClient
from core.orderbook_searcher import OrderbookSearcher
from core.price_oracle import PriceOracle
from core.trade_executor import TradeExecutor
from core.tradind_config import TradingConfig
from core.trading_manager import TradingManager
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

symbol = 'SCR'
badget = 2

bybit_ccxt_pro_client = ccxt_pro.bybit({
    'apiKey': os.getenv('BYBIT_KEY'),
    'secret': os.getenv('BYBIT_SECRET'),
    'options': { 'recvWindow': 7000 },  # default 5000
})

hyperliquid_ccxt_pro_client = ccxt_pro.hyperliquid({
    'walletAddress': os.getenv('HYLIQ_ADDRESS'),
    'privateKey': os.getenv('HYLIQ_SECRET'),
})

bybit_client = BybitClient(bybit_ccxt_pro_client)    
hyperliquid_client = HyperliquidClient(hyperliquid_ccxt_pro_client)
trading_config = TradingConfig(symbol=symbol, badget=badget, delta=0.01)
price_oracle = PriceOracle(bybit_client, hyperliquid_client)
trade_executor = TradeExecutor(bybit_client, hyperliquid_client)
trading_manager = TradingManager(trading_config, price_oracle, trade_executor)
orderbook_searcher = OrderbookSearcher(symbol=symbol, ccxt_bybit_client=bybit_ccxt_pro_client, ccxt_hyperliquid_client=hyperliquid_ccxt_pro_client)

logger.info('start running bot')
asyncio.run(trading_manager.start_search(orderbook_searcher))
logger.info('end running bot')
