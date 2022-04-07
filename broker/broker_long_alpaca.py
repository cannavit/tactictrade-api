import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si
from transaction.models import transactions

import alpaca_trade_api as tradeapi
from broker.models import alpaca_configuration
from utils.transform_strings.stringConvert import delete_char
from utils.brokers.broker_alpaca import broker_alpaca


def broker_buy_alpaca(options, strategy, trading, results, mockate=False):

    alpaca = alpaca_configuration.objects.get(broker_id=trading.broker.id)

    api = tradeapi.REST(alpaca.APIKeyID, alpaca.SecretKey, alpaca.endpoint)

    if options['brokerCapital'] < options['quantityUSD']:
        return {
            'status': 'error',
            'message': 'The capital is not enough to buy the stock'
        }

    price = si.get_live_price(options['symbol'])

    symbol = delete_char(options['symbol'], '-')

    trasactionLast = transactions.objects.filter(
        owner_id=trading.owner.id,
        strategyNews_id=strategy.id,
        broker_id=trading.broker.id,
        symbol_id=strategy.symbol.id,
        operation='long',
        is_paper_trading__in=[True],
        broker=trading.broker,
        isClosed__in=[False]
    ).order_by('-id')

    if trasactionLast.count() == 0:  # Open The Transaction

        # TODO add the options of use too qty, take_profit, stop_loss
        responseAlpaca = broker_alpaca(api).open_long_trade(
            symbol=symbol,
            qty=None,
            notional=trading.quantityUSDLong,
            stop_loss=None,
            stop_loss_porcent=trading.stopLossLong,
            take_profit=None,
            take_profit_porcent=trading.takeProfitLong,
            price=price
        )

        responseAlpaca = responseAlpaca['response']

        if responseAlpaca.get('status') != 'accepted' and responseAlpaca.get('status') != 'success':

            return {
                'status': 'error',
                'message': 'Not was possible to open the transaction in alpaca'
            }


        transactions.objects.create(
            owner_id=trading.owner.id,
            strategyNews_id=strategy.id,
            broker_id=trading.broker.id,
            symbol_id=strategy.symbol.id,
            is_paper_trading=True,
            order=options['order'],
            operation='long',
            # qty_open=qty,
            # price_open=price_open,
            isClosed=False,
            stop_loss=options['stopLoss'],
            take_profit=options['takeProfit'],
            base_cost=options['quantityUSD'],
            idTransaction=responseAlpaca.id,
            status='accepted_alpaca',
        )

        results['long']['transaction_opened'] = results['long']['transaction_opened'] + 1
        results['long']['follower_id_opened'].append(trading.owner.id)
        results['long']['symbol'] = options['symbol']
        results['long']['spread'] = '-1'
        results['long']['response'] = {
            'status': 'success',
            'message': 'The transaction was opened in alpaca with success',
        }

    else:
        return {
            'status': 'error',
            'message': 'The position is open in alpaca',
        }
