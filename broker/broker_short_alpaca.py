import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si
from transaction.models import transactions

import alpaca_trade_api as tradeapi
from broker.models import alpaca_configuration
from utils.transform_strings.stringConvert import delete_char
from utils.brokers.broker_alpaca import broker_alpaca


def broker_sell_short_alpaca(options, strategy, trading, results):

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
                    operation='short',
                    is_paper_trading__in=[True],
                    broker=trading.broker,
                    isClosed__in=[False]
                ).order_by('-id')

    if trasactionLast.count() == 0: # Open The Transaction

        responseAlpaca = broker_alpaca(api).open_short_trade(
            symbol=symbol,
            qty=trading.initialCapitalUSDShort,
            notional=None,
            stop_loss=None,
            stop_loss_porcent=trading.stopLossShort,
            take_profit=None,
            take_profit_porcent=trading.takeProfitShort,
            price=price
        )

        if responseAlpaca['status'] != 'accepted':
            return {
                'status': 'error',
                'message': responseAlpaca['message']
            }

        responseAlpaca = responseAlpaca['response']
        

        qty = float(responseAlpaca.qty)
        price_open = float(responseAlpaca.qty)
        base_cost = qty * price_open

        # Get Open Position Alpaca Using responseAlpaca.id
        transactions.objects.create(
            owner_id=trading.owner.id,
            strategyNews_id=strategy.id,
            broker_id=trading.broker.id,
            symbol_id=strategy.symbol.id,
            is_paper_trading=True,
            order=options['order'],
            operation='short',
            qty_open=responseAlpaca.qty,
            base_cost=base_cost,
            price_open=price_open,
            isClosed=False,
            stop_loss=options['stopLoss'],
            take_profit=options['takeProfit'],
            idTransaction=responseAlpaca.id,
        )

        results['short']['transaction_opened'] = results['long']['transaction_opened'] + 1
        results['short']['follower_id_opened'].append(trading.owner.id)
        results['short']['symbol'] = options['symbol']
        results['short']['spread'] = '-1'
        results['short']['qty'] = qty
        results['short']['price_open'] = price_open
        results['short']['base_cost'] = base_cost
        results['short']['response'] = {
            'status': 'success',
            'message': 'The transaction was opened in alpaca with success',
        }


    else:
        return {
            'status': 'error',
            'message': 'The position is open in alpaca',
        }