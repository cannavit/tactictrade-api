import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si
from apps.transaction.models import transactions
from apps.transaction.serializers import TransactionSelectSerializersCreate


class papertrade:

    # Define self data
    def __init__(self, trading, strategy, operation='long'):

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

        self.isClosed = False
        if self.count != 0:
            self.isClosed = self.trasactionLast.values()[0]['isClosed']

    def create_transaction(self, options={}):

            data = {
                "owner_id": self.trading.owner.id,
                "strategyNews_id": self.strategy.id,
                "broker_id": self.trading.broker.id,
                "symbol_id": self.strategy.symbol.id,
                "is_paper_trading": True,
                "order": options['order'],
                "operation": self.operation,
                "isClosed": False,
                "stop_loss": options['stopLoss'],
                "take_profit": options['takeProfit'],
                "base_cost": options['quantityUSD'],
            }

            transactions.objects.create(
                **data
            )


    def return_results(self,options={}, results={}):

        results[self.operation]['transaction_opened'] = results[self.operation]['transaction_opened'] + 1
        results[self.operation]['follower_id_opened'].append(
            self.trading.owner.id)
        results[self.operation]['symbol'] = options['symbol']

        return results

    # Close operation in paper trade for long.
    def long_buy(self, options={},results={}):

        if self.count == 0 or self.isClosed == True:
            self.create_transaction(self.options, self.results)

        results = self.return_results(options, results)

        return results

    # Close operation in paper trade for long. 
    def long_sell(self, options={}, results={}):

        if self.count > 0 and self.isClosed == False:

            self.trasactionLast.update(
                isClosed=True,
                status='transactions_updated_calculate_profit'
            )

        results = self.return_results(options, results)

        return results

    # Open operation in paper trade with short. 
    def short_buy(self, results={}):

        if self.count == 0 and self.isClosed == False:

            self.create_transaction(self.options, self.results)

        results = self.return_results(self.options, self.results)

        return results


    def short_sell(self, options={},results={}):

        if self.count == 0 or self.isClosed == False: 
                
            self.create_transaction(options, results)

        results = self.return_results(options, results)

        return results

        
