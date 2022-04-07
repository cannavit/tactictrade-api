import alpaca_trade_api as tradeapi
import requests


class AlpacaTrading(object):
    
    def buy(self, API_KEY, SECRET_KEY, BASE_URL,SYMBOL, QTY_USD):
        # Get API Key

        api = tradeapi.REST(API_KEY, SECRET_KEY,BASE_URL)

        response = api.submit_order(
                 side='buy',
                 symbol=SYMBOL,
                 type="market",
                 qty=None,
                 notional=QTY_USD,
                 time_in_force="day"
            )

        return response

    def sell(self, API_KEY, SECRET_KEY, BASE_URL,SYMBOL, QTY_USD):
        # Get API Key

        api = tradeapi.REST(API_KEY, SECRET_KEY,BASE_URL)

        response = api.submit_order(
                 side='sell',
                 symbol=SYMBOL,
                 type="market",
                 qty=None,
                 notional=QTY_USD,
                 time_in_force="day"
            )

        return response
