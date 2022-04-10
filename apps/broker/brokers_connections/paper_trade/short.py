import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si
from apps.transaction.models import transactions
from apps.transaction.serializers import TransactionSelectSerializersCreate

class broker:

    # Define self data
    def __init__(self, trading, strategy, operation='short', options={}, results={}):

        self.trasactionLast = transactions.objects.filter(
            owner_id=trading.owner.id,
            strategyNews_id=strategy.id,
            broker_id=trading.broker.id,
            symbol_id=strategy.symbol.id,
            operation=operation,
            is_paper_trading__in=[True],
        ).order_by('-id')

        self.count = self.trasactionLast.count()
        self.trading = trading
        self.operation = operation
        self.strategy = strategy

        self.options = options
        self.results = results

        self.have_transaction_open = False

        if self.count > 0:
            self.have_transaction_open = True

        self.price = si.get_live_price(self.options.symbol)

    def create_transaction(self, options={}):

            data = {
                "owner_id": self.trading.owner.id,
                "strategyNews_id": self.strategy.id,
                "broker_id": self.trading.broker.id,
                "symbol_id": self.strategy.symbol.id,
                "is_paper_trading": True,
                "order": options.order,
                "operation": self.operation,
                "isClosed": False,
                "stop_loss": options.stopLoss,
                "take_profit": options.takeProfit,
                "base_cost": options.quantityUSD,
            }

            transactions.objects.create(
                **data
            )

    def return_results(self,options={}, results={}):

        results[self.operation]['transaction_opened'] = results[self.operation]['transaction_opened'] + 1
        results[self.operation]['follower_id_opened'].append(
            self.trading.owner.id)
        results[self.operation]['symbol'] = options.symbol

        return results

    # Open operation in paper trade with short. 
    def short_buy(self):

        if self.count == 0 and self.have_transaction_open == False:

            self.create_transaction(self.options)

        results = self.return_results(self.options, self.results)

        return results

        
    # Close operation in paper trade for long. 
    def close_position(self):

        if self.count > 0 and self.have_transaction_open:

            self.trasactionLast.update(
                price_closed=self.price,
                isClosed=True,
                status='transactions_updated_calculate_profit'
            )

        results = self.return_results(self.options, self.results)

        return results


# # def broker_short_sell_papertrade(options, strategy, trading, results):

#     #TODO to optimize THIS PART IS REPEATED IN broker_long_papertrade.py
#     trasactionLast = transactions.objects.filter(
#                     owner_id=trading.owner.id,
#                     strategyNews_id=strategy.id,
#                     broker_id=trading.broker.id,
#                     symbol_id=strategy.symbol.id,
#                     operation='short',
#                     is_paper_trading=True,
#                 ).order_by('-id')


#     if self.have_transaction_open:
#         isClosed = trasactionLast.values()[0]['isClosed']


#     if count == 0 or isClosed == True: 

#         price = si.get_live_price(options['symbol'])
#         spread = 0.78
#         qty = (options['quantityUSD'] - spread) / price

#         number_stock = options['quantityUSD'] / price

#         transactions.objects.create(
#             owner_id=trading.owner.id,
#             strategyNews_id=strategy.id,
#             broker_id=trading.broker.id,
#             symbol_id=strategy.symbol.id,
#             is_paper_trading=True,
#             order=options['order'],
#             operation='short',
#             qty_open=qty,
#             price_open=price,
#             isClosed=False,
#             stop_loss=options['stopLoss'],
#             take_profit=options['takeProfit'],
#             base_cost=options['quantityUSD'], 
#             number_stock=number_stock,
#         )

#         results['short']['transaction_opened'] = results['short']['transaction_opened'] + 1
#         results['short']['follower_id_opened'].append(trading.owner.id)
#         results['short']['symbol'] = options['symbol']
#         results['short']['spread'] = spread
#         results['short']['qty'] = qty
#         results['short']['price_open'] = price
#         # number_stocks
#         results['short']['number_stock'] = number_stock

#         return results


# def broker_short_buy_papertrade(options, strategy, trading, results):

#     trasactionLast = transactions.objects.filter(
#                     owner_id=trading.owner.id,
#                     strategyNews_id=strategy.id,
#                     broker_id=trading.broker.id,
#                     symbol_id=strategy.symbol.id,
#                     operation='short',
#                     is_paper_trading=True,
#                 ).order_by('-id')

#     count = trasactionLast.count()

#     isClosed = False
#     if count != 0:
#         isClosed = trasactionLast.values()[0]['isClosed']


#     if count == 0 or isClosed == False: 
#         print(count)

#         price = si.get_live_price(options['symbol'])
        
#         data = trasactionLast.values()
#         data = data[0]


#         base_cost = trading['initialCapitalUSDShort'] * price



#         # base_cost = data['base_cost']

#         price_short = data['number_stock'] * price
#         # profit = base_cost - price_short
#         # current_value = base_cost+ profit
#         # profit_percentage = (current_value  - base_cost)/base_cost
#         # profit_percentage = profit_percentage * 100

#         trasactionLast.update(
#             base_cost=base_cost,
#             # profit_percentage=profit_percentage,
#             isClosed=True,
#             price_closed=price,
#             status='transactions_updated_calculate_profit'
#         )



#         results['short']['transaction_closed'] = results['short']['transaction_closed'] + 1
#         results['short']['follower_id_closed'].append(trading.owner.id)
#         results['short']['symbol'] = options['symbol']
#         # results['short']['profit'] = profit
#         # results['short']['profit_percentage'] = profit_percentage
