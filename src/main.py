import asyncio
import os

import ccxt.pro as ccxt_pro
from client.bybit_client import BybitClient
from client.hyperliquid_client import HyperliquidClient
from core.notifier import Notifier
from core.price_oracle import PriceOracle
from core.trade_executor import TradeExecutor
from core.trading_manager import TradingConfig, TradingManager
from dotenv import load_dotenv

load_dotenv()

symbol = 'SCRUSDT'
badget = 2

bybit_ccxt_pro_client = ccxt_pro.bybit({
    'apiKey': os.getenv('BYBIT_KEY'),
    'secret': os.getenv('BYBIT_SECRET'),
    'options': { 'recvWindow': 7000 },  # default 5000
})

hyperliquid_ccxt_pro_client = ccxt_pro.hyperliquid()

bybit_client = BybitClient(bybit_ccxt_pro_client)    
hyperliquid_client = HyperliquidClient(hyperliquid_ccxt_pro_client)
price_oracle = PriceOracle(bybit_client, hyperliquid_client)
executor = TradeExecutor(bybit_client, hyperliquid_client)
trading_config = TradingConfig(symbol=symbol, badget=badget)
trading_manager = TradingManager(trading_config, executor, price_oracle)
contract_notifier = Notifier(trading_manager, bybit_client, hyperliquid_client)
trading_manager.attach_notifier(contract_notifier)

print('start running bot')
asyncio.run(trading_manager.run())
print('end running bot')
