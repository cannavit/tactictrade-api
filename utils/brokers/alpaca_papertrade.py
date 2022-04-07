import alpaca_trade_api as tradeapi
from broker_alpaca import broker_alpaca


class papertrade_alpaca():

    def __init__(self, api, type=None):

        self.api = api
        self.type = type

    def long_buy(self, symbol, qty=None, national=None):
        
        print('SYMBOL: ', symbol)
        print('QTY: ', qty)
        print('NATIONAL: ', national)

        # Close all old operations 
        broker_alpaca(self.api).close_all_positions_opened()

        response = broker_alpaca(self.api).open_long_trade(symbol=symbol, qty=qty)

        response_opened = response['response']
        print(response_opened.id)
        print("@Note-01 ---- 253007614 -----")
        print(qty)
        print("@Note-01 ---- -96031010 -----")
        print(response)


APIKeyID = "PKYXXACZ8GNCGN6QIXBW"
SecretKey = "ebXGVxLNc0arjPwNK9OcPREsgwd7l2MApp48MHHm"
endpoint = "https://paper-api.alpaca.markets"

api = tradeapi.REST(APIKeyID, SecretKey, endpoint)

papertrade_alpaca(api).long_buy(symbol='SOLUSD', qty=1, national=1000)


# response = broker_alpaca(api).open_long_trade(
#     symbol='ETHUSD',
#     # qty=1,
#     notional=400,
#     stop_loss=None,
#     stop_loss_porcent=-5,
#     take_profit=None,
#     take_profit_porcent=10,
#     price=si.get_live_price('ETH-USD'),
# )