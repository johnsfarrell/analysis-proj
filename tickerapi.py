from stocksymbol import StockSymbol
import os
#import tickers

ss = StockSymbol(os.getenv("STOCKSYMBOL_API_KEY"))
Tickers =  ss.get_symbol_list("US", symbols_only=True)