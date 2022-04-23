# Import alpaca library
from re import A
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
from django.forms import ValidationError
from yahoo_fin import stock_info as si
import json

from utils.convert_json_to_objects import convertJsonToObject



def close_orders_opened(api, SYMBOL):

    list_orders = api.list_orders()

    responseList = []
    for order in list_orders:
        # order = list_orders[key]
        response = api.cancel_order(order.id)
        responseList.append(response)

    return responseList


class broker_alpaca_lib:

    def __init__(self, api, type=None, symbol=None, price=None):

        self.api = api
        self.type = type
        self.symbol = symbol

        self.price = price
        if price == None:
            self.prince = si.get_live_price(symbol)

    def get_position(self, id):

        orders = self.api.get_order(id)
        symbol = orders.symbol

        try:
            positions = self.api.get_position(symbol)
        except Exception as e:

            return {
                'error_type': 'position_not_exists',
                'status': orders.status,
                'message': str(e),
                'emisor': 'broker_alpaca',
                'response': orders
            }

        market_value = float(positions.market_value)
        qty = float(orders.filled_qty)
        cost_basis = float(positions.cost_basis)

        accion_open_price = qty * cost_basis

        current_price = float(positions.current_price)

        data = {}
        if self.type == 'long':

            profit_total = market_value - cost_basis
            profit_porcent = 1 - (cost_basis - profit_total)/cost_basis
            profit_porcent = profit_porcent * 100

        elif self.type == 'short':

            profit_total = abs(cost_basis) - abs(market_value)
            profit_porcent = (cost_basis - market_value)/market_value

        # open_price = current_price  +  current_price * profit_porcent
        
        

        response = {
            "status": orders.status,
            "data": {
                "symbol": symbol,
                "qty": qty,
                "market_value": abs(market_value),
                "profit_total": profit_total,
                "profit_porcent": profit_porcent,
                "cost_basis": abs(cost_basis),
                "accion_open_price": accion_open_price,
                "current_price": current_price,
                # "open_price": positions.current_price * ,
            }
        }

        return convertJsonToObject(response)

    def close_position(self, id):

        orders = self.api.get_order(id)
        symbol = orders.symbol
        qty = orders.qty

        # Cancel all orders open related with that symbol
        response = close_orders_opened(self.api, symbol)

        if orders.side == 'buy':
            side = 'sell'
        elif orders.side == 'sell':
            side = 'buy'

        try:

            response = self.api.submit_order(
                client_order_id=id,
                side=side,
                symbol=symbol,
                qty=orders.filled_qty,
                type="market",
                time_in_force="day"
            )

        except Exception as e:

            return {
                'status': 'error',
                'message': str(e),
            }

        if response.status != 'accepted':
            return {
                'status': 'error',
                'message': 'Not was possible to close the transaction in alpaca',
                'response': response
            }

        data = convertJsonToObject({
            'status': 'success',
            'message': 'The transaction was closed in alpaca',
        })

        data.response = response

        return data

    def long_buy(self,
                 qty=None,
                 notional=None,
                 stop_loss=None,
                 stop_loss_porcent=None,
                 take_profit=None,
                 take_profit_porcent=None,
                 broker=None,
                 ):

        stop_loss_option = None

        if stop_loss_porcent is not None:
            stop_loss = self.price - self.price * \
                float(abs(stop_loss_porcent)) * 0.01

        if stop_loss is not None:
            stop_loss_option = dict(
                stop_price=stop_loss,
                limit_price=stop_loss,
            )

        take_profit_option = None
        if take_profit_porcent is not None:
            take_profit = self.price + self.price * \
                float(take_profit_porcent) * 0.01

        if take_profit is not None:
            take_profit_option = dict(
                limit_price=take_profit,
            )

        response = {}

        if notional == 0.0:
            notional = None

        if qty == 0.0:
            qty = None

        if take_profit_option is not None and stop_loss_option is not None:

            try:
                response = self.api.submit_order(
                    symbol=self.symbol,
                    side='buy',
                    type='market',
                    qty=qty,
                    notional=notional,
                    time_in_force='day',
                    order_class='bracket',
                    take_profit=take_profit_option,
                    stop_loss=stop_loss_option
                )
            except Exception as e:
                try:
                    response = self.api.submit_order(
                        symbol=self.symbol,
                        side='buy',
                        type='market',
                        qty=qty,
                        notional=notional,
                        time_in_force='day',
                        order_class='simple',
                        take_profit=take_profit_option,
                        stop_loss=stop_loss_option
                    )
                except Exception as e:
                    raise ValidationError("Error in Alpaca Long Buy: " + str(e))

        elif take_profit_option is None and stop_loss_option is not None:

            response = self.api.submit_order(
                symbol=self.symbol,
                side='buy',
                type='market',
                qty=qty,
                notional=notional,
                time_in_force='day',
                order_class='oto',
                stop_loss=stop_loss_option
            )

        elif take_profit_option is not None and stop_loss_option is None:

            return {
                'status': 'error',
                'message': 'Bracket orders require stop_loss or take_profit',
                'emisor': 'broker_alpaca'
            }

        else:

            response = self.api.submit_order(
                symbol=self.symbol,
                side='buy',
                type='market',
                qty=qty,
                notional=notional,
                time_in_force='day',
                take_profit=take_profit_option,
                stop_loss=stop_loss_option
            )

        try:
            if response.get('status') != 'accepted' or response.get('status') == None:
                return {
                    'status': 'error',
                    'message': 'Not was possible to open the transaction in alpaca',
                    'emisor': 'broker_alpaca',
                    'response': response
                }
        except Exception as e:
            print(e)

        data = {
                'id': response.id,
                'symbol': self.symbol,
                'qty': qty,
                'notional': notional,
                'stop_loss': stop_loss,
                'stop_loss_porcent': stop_loss_porcent,
                'take_profit': take_profit,
                'take_profit_porcent': take_profit_porcent,
                'type': 'long'
            }
        # Convert JSON to string

        response = {
            'status': 'success',
            'message': 'The operation was open in alpaca',
            'emisor': 'broker_alpaca',
            'data': data,
            # 'response': response
        }


        # Convert response in one objects
        response = convertJsonToObject(response)

        response.response= response

        return response

    def get_open_positions(self):

        response = self.api.list_positions()
        data = []

        for position in response:

            data.append({
                'id': position.asset_id,
                'symbol': position.symbol,
                'qty': position.qty,
                'current_price': position.current_price,
                'cost_basis': position.cost_basis,
                'change_today': position.change_today,
                'type': position.side,
            })

        return {
            'status': 'success',
            'message': 'List of positions opened in alpaca',
            'emisor': 'broker_alpaca',
            'data': data
        }

    def open_short_trade(self,
                         symbol,
                         qty=None,
                         notional=None,
                         stop_loss=None,
                         stop_loss_porcent=None,
                         take_profit=None,
                         take_profit_porcent=None,
                         price=None,
                         ):

        if price is None:
            price = si.get_live_price(symbol)

        stop_loss_option = None
        if stop_loss_porcent is not None:
            stop_loss = price + price * float(abs(stop_loss_porcent)) * 0.01

        if stop_loss is not None:
            stop_loss_option = dict(
                stop_price=stop_loss,
                limit_price=stop_loss,
            )

        print(stop_loss_option)

        take_profit_option = None
        if take_profit_porcent is not None:
            take_profit = price - price * float(take_profit_porcent) * 0.01

        if take_profit is not None:
            take_profit_option = dict(
                limit_price=take_profit,
            )

        if notional == 0.0:
            notional = None
        if qty == 0.0:
            qty = None

        response = {}

        if take_profit_option is not None and stop_loss_option is not None:

            try:
                response = self.api.submit_order(
                    side='sell',
                    symbol=symbol,
                    type='market',
                    qty=qty,
                    notional=notional,
                    time_in_force='day',
                    # order_class='bracket',
                    # take_profit=take_profit_option, #TODO Check how use take_profit
                    # stop_loss=stop_loss_option
                )

            except Exception as e:

                try:
                    response = self.api.submit_order(
                        symbol=symbol,
                        side='sell',
                        type='market',
                        qty=qty,
                        notional=notional,
                        time_in_force='day',
                        order_class='simple',
                        take_profit=take_profit_option,
                        stop_loss=stop_loss_option
                    )
                except Exception as e:
                    return {
                        'status': 'error',
                        'message': str(e),
                        'emisor': 'broker_alpaca'
                    }

        elif take_profit_option is None and stop_loss_option is not None:

            response = self.api.submit_order(
                symbol=symbol,
                side='sell',
                type='market',
                qty=qty,
                notional=notional,
                time_in_force='day',
                order_class='oto',
                stop_loss=stop_loss_option
            )

        elif take_profit_option is not None and stop_loss_option is None:

            return {
                'status': 'error',
                'message': 'Bracket orders require stop_loss or take_profit',
                'emisor': 'broker_alpaca'
            }

        else:

            response = self.api.submit_order(
                symbol=symbol,
                side='sell',
                type='market',
                qty=qty,
                notional=notional,
                time_in_force='day',
                take_profit=take_profit_option,
                stop_loss=stop_loss_option
            )

        if response.status != 'accepted':
            return {
                'status': 'error',
                'message': 'Not was possible to open the transaction in alpaca',
                'emisor': 'broker_alpaca',
                'response': response
            }

        return {
            'status': 'success',
            'message': 'The operation was open in alpaca',
            'emisor': 'broker_alpaca',
            'data': {
                'id': response.id,
                'symbol': symbol,
                'qty': qty,
                'notional': notional,
                'stop_loss': stop_loss,
                'stop_loss_porcent': stop_loss_porcent,
                'take_profit': take_profit,
                'take_profit_porcent': take_profit_porcent,
                'type': 'short'
            },
            'response': response
        }

    # Close all positions in alapca trade.
    def close_all_positions_opened(self):

        response = self.api.close_all_positions()

        return {
            'status': 'success',
            'message': 'All positions were closed in alpaca',
            'emisor': 'broker_alpaca',
            'response': response
        }

# APIKeyID = "PK5BTT3MCFGTT231CU3B"
# SecretKey = "kX9sLd7zTXGsUBVknYqjCLhjcj62reF5nsa4MDc2"
# endpoint = "https://paper-api.alpaca.markets"
# api = tradeapi.REST(APIKeyID, SecretKey, endpoint)

# broker_alpaca(api).close_all_positions()


# id = '4cf3507d-4217-47f0-bb52-f8b803ea9b42'
# data = broker_alpaca(api, 'short').get_position(id)
# print(data)

# id = '12cb6a50-4b24-4b0a-a69c-df850d96d3ee'
# data = broker_alpaca(api, 'long').get_position(id)
# print(data)

# id = '94691700-669a-4af6-9c28-0f9486f9193b'
# 'client_order_id':'16835af0-4eca-42cc-ae04-1a0bf5c94524'

# response = broker_alpaca(api).close_position(id)
# print(response)


# response = broker_alpaca(api).long_buy(
#     symbol='ETHUSD',
#     # qty=1,
#     notional=400,
#     stop_loss=None,
#     stop_loss_porcent=-5,
#     take_profit=None,
#     take_profit_porcent=10,
#     price=si.get_live_price('ETH-USD'),
# )

# response = broker_alpaca(api).get_open_positions()
# print(response)


# TEST OPEN ONE SHORT POSITION

# response = broker_alpaca(api).open_short_trade(
#     symbol='MSFT',
#     qty=1,
#     notional=None,
#     stop_loss=None,
#     stop_loss_porcent=-5,
#     take_profit=None,
#     take_profit_porcent=10,
#     # price=si.get_live_price('ETH-USD'),
# )

# print(response)

# id = 'c6baed93-3460-4533-9083-e500950d7e60'
# id = '744894e1-c0f7-41f8-b32c-f9680c0eac9d'
# # Get Position Type
# data = broker_alpaca(api, 'long').get_position(id)
# print('--------------------------- PROFIT DATA ---------------------------')
# print(data)

# # # # Close Position
# response = broker_alpaca(api).close_position(id)
# print('--------------------------- CLOSE POSITION ---------------------------')
# print(response)
