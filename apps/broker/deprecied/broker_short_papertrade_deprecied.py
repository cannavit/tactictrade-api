import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si
from apps.transaction.models import transactions

def broker_short_sell_papertrade(options, strategy, trading, results):

    #TODO to optimize THIS PART IS REPEATED IN broker_long_papertrade.py
    trasactionLast = transactions.objects.filter(
                    owner_id=trading.owner.id,
                    strategyNews_id=strategy.id,
                    broker_id=trading.broker.id,
                    symbol_id=strategy.symbol.id,
                    operation='short',
                    is_paper_trading=True,
                ).order_by('-id')

    count = trasactionLast.count()

    isClosed = False
    if count != 0:
        isClosed = trasactionLast.values()[0]['isClosed']


    if count == 0 or isClosed == True: 

        price = si.get_live_price(options['symbol'])
        spread = 0.78
        qty = (options['quantityUSD'] - spread) / price

        number_stock = options['quantityUSD'] / price

        transactions.objects.create(
            owner_id=trading.owner.id,
            strategyNews_id=strategy.id,
            broker_id=trading.broker.id,
            symbol_id=strategy.symbol.id,
            is_paper_trading=True,
            order=options['order'],
            operation='short',
            qty_open=qty,
            price_open=price,
            isClosed=False,
            stop_loss=options['stopLoss'],
            take_profit=options['takeProfit'],
            base_cost=options['quantityUSD'], 
            number_stock=number_stock,
        )

        results['short']['transaction_opened'] = results['short']['transaction_opened'] + 1
        results['short']['follower_id_opened'].append(trading.owner.id)
        results['short']['symbol'] = options['symbol']
        results['short']['spread'] = spread
        results['short']['qty'] = qty
        results['short']['price_open'] = price
        # number_stocks
        results['short']['number_stock'] = number_stock

        return results


def broker_short_buy_papertrade(options, strategy, trading, results):

    trasactionLast = transactions.objects.filter(
                    owner_id=trading.owner.id,
                    strategyNews_id=strategy.id,
                    broker_id=trading.broker.id,
                    symbol_id=strategy.symbol.id,
                    operation='short',
                    is_paper_trading=True,
                ).order_by('-id')

    count = trasactionLast.count()

    isClosed = False
    if count != 0:
        isClosed = trasactionLast.values()[0]['isClosed']


    if count == 0 or isClosed == False: 

        price = si.get_live_price(options['symbol'])
        
        data = trasactionLast.values()
        data = data[0]


        base_cost = trading['initialCapitalUSDShort'] * price



        # base_cost = data['base_cost']

        price_short = data['number_stock'] * price
        # profit = base_cost - price_short
        # current_value = base_cost+ profit
        # profit_percentage = (current_value  - base_cost)/base_cost
        # profit_percentage = profit_percentage * 100

        trasactionLast.update(
            base_cost=base_cost,
            # profit_percentage=profit_percentage,
            isClosed=True,
            price_closed=price,
            status='transactions_updated_calculate_profit'
        )



        results['short']['transaction_closed'] = results['short']['transaction_closed'] + 1
        results['short']['follower_id_closed'].append(trading.owner.id)
        results['short']['symbol'] = options['symbol']
        # results['short']['profit'] = profit
        # results['short']['profit_percentage'] = profit_percentage
