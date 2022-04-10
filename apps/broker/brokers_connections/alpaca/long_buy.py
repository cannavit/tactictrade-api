import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si

from apps.broker.models import alpaca_configuration
from apps.transaction.models import transactions
from utils.brokers.broker_alpaca import broker_alpaca_lib
from utils.convert_json_to_objects import convertJsonToObject
from utils.transform_strings.stringConvert import delete_char


def control_liquidity(self):

    if self.options.brokerCapital < self.options.quantityUSD:
        return {
            'status': 'error',
            'message': 'The capital is not enough to buy the stock'
        }
    else:
        return {}


class broker():

    # init data
    def __init__(self, options, strategy, trading, results, operation='long'):

        self.options = options
        self.strategy = strategy
        self.trading = trading
        self.results = results
        self.operation = operation

        self.alpaca = alpaca_configuration.objects.get(
            broker_id=trading.broker.id)
        self.api = tradeapi.REST(self.alpaca.APIKeyID,
                                 self.alpaca.SecretKey, self.alpaca.endpoint)

        liquidity = control_liquidity(self)
        if liquidity.get('status') == 'error':
            return liquidity

        self.trasactionLast = transactions.objects.filter(
            owner_id=trading.owner.id,
            strategyNews_id=strategy.id,
            broker_id=trading.broker.id,
            symbol_id=strategy.symbol.id,
            operation=operation,
            broker=trading.broker,
            isClosed__in=[False]
        ).order_by('-id')

        count = self.trasactionLast.count()
        self.have_transaction_open = False

        self.symbol = strategy.symbol.symbolName
        self.symbol_corrected = strategy.symbol.symbolName_corrected
        self.price = si.get_live_price(self.symbol_corrected)

        # self.symbol_corrected

        if count > 0:
            self.have_transaction_open = True

        self.is_crypto = self.strategy.symbol.is_crypto

    def long_buy(self):

        if not self.have_transaction_open:

            responseAlpaca = broker_alpaca_lib(self.api,
                                               symbol=self.symbol, price=self.price).long_buy(
                qty=self.trading.quantityQTYLong,
                notional=self.trading.quantityUSDLong,
                stop_loss_porcent=self.trading.stopLossLong,
                take_profit_porcent=self.trading.takeProfitLong,
                broker=self.trading.broker,
            )

            if responseAlpaca.status != 'accepted' and responseAlpaca.status != 'success':
                return {
                    'status': 'error',
                    'message': 'Not was possible to open the transaction in alpaca'
                }

            transactions.objects.create(
                owner_id=self.trading.owner.id,
                strategyNews_id=self.strategy.id,
                broker_id=self.trading.broker.id,
                symbol_id=self.strategy.symbol.id,
                is_paper_trading=self.trading.is_paper_trading,
                order=self.options.order,
                operation=self.operation,
                isClosed=False,
                stop_loss=responseAlpaca.data.stop_loss_porcent,
                stop_loss_qty=responseAlpaca.data.stop_loss,
                take_profit=responseAlpaca.data.take_profit_porcent,
                take_profit_qty=responseAlpaca.data.take_profit,
                base_cost=self.options.quantityUSD,
                idTransaction=responseAlpaca.response.data.id,
                status='accepted_alpaca', # This status is for verify the transaction with scheduler task in alpaca
            )

            self.results[self.operation]['transaction_opened'] = self.results['long']['transaction_opened'] + 1
            self.results[self.operation]['follower_id_opened'].append(
                self.trading.owner.id)
            self.results[self.operation]['symbol'] = self.options.symbol
            self.results[self.operation]['spread'] = '-1'
            self.results[self.operation]['response'] = {
                'status': 'success',
                'message': 'The transaction was opened in alpaca with success',
            }

            return self.results

        else:

            return convertJsonToObject({
                'status': 'error',
                'message': 'The position is open in alpaca',
            })
