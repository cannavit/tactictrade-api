import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si

from apps.broker.models import alpaca_configuration
from apps.transaction.models import transactions
from utils.brokers.broker_alpaca import broker_alpaca_lib
from utils.calculate_porcentaje import pct_change
from utils.convert_json_to_objects import convertJsonToObject
from utils.transform_strings.stringConvert import delete_char


def get_alpaca_percentage_profit_closed(api, idTransaction,basic_cost):

    alpaca_list_order = api.list_orders(
        status='closed',
        limit=100,
        nested=True
    )

    print(alpaca_list_order)
    order_list_closed = []
    for order in alpaca_list_order:
        if order.id == idTransaction or order.asset_id == idTransaction or order.client_order_id == idTransaction:
            print(order)
            order_list_closed.append(order)

    if len(order_list_closed) < 2:
        return {
            'status': 'error',
            'message': 'Not was possible to close the transaction in alpaca'
        }

        # print(order)

    amount_closed_open = float(
        order_list_closed[0]._raw['filled_avg_price']) * float(order_list_closed[0]._raw['filled_qty'])
    amount_closed_closed = float(
        order_list_closed[1]._raw['filled_avg_price']) * float(order_list_closed[1]._raw['filled_qty'])

    # profit = amount_closed_open - amount_closed_closed
    profit = basic_cost - amount_closed_closed

    profit_percentage = pct_change(
        amount_closed_closed, amount_closed_open)
    profit_percentage = round(profit_percentage, 3)


    return convertJsonToObject({
        'profit': profit,
        'profit_percentage': profit_percentage,
        'symbol': order_list_closed[0].symbol,
        'qty': order_list_closed[0]._raw['filled_qty'],
        'side': order_list_closed[0]._raw['side'],
        'price': amount_closed_closed,
        'close_price': float(order_list_closed[0]._raw['filled_avg_price']),
        'qty_close': float(order_list_closed[0]._raw['filled_qty']),
        # 'is_winner': is_winner
    })




def broker_close_trade_alpaca(options, strategy, trading, results, operation):


    alpaca = alpaca_configuration.objects.get(broker_id=trading.broker.id)

    api = tradeapi.REST(alpaca.APIKeyID, alpaca.SecretKey, alpaca.endpoint)

    if options['brokerCapital'] < options['quantityUSD']:
        return {
            'status': 'error',
            'message': 'The capital is not enough to buy the stock'
        }

    # Open Long
    trasactionLast = transactions.objects.filter(
        owner_id=trading.owner.id,
        strategyNews_id=strategy.id,
        broker_id=trading.broker.id,
        symbol_id=strategy.symbol.id,
        operation=operation,
        is_paper_trading__in=[True],
        broker=trading.broker,
        isClosed__in=[False]
    ).order_by('-id')

    count = trasactionLast.count()

    transaction_open = trasactionLast.count()
    closeOperation = False

    # if  transaction_open != 0 and operation == 'short' : # Close the long The Transaction
    if transaction_open != 0:  # Close the long The Transaction
        print(count)
        closeOperation = True

    if transaction_open != 0 and operation == 'long':  # Open The Transaction
        closeOperation = True

    if closeOperation:
        data = trasactionLast.values()[0]
        # Close position
        responseAlpacaPosition = broker_alpaca_lib(api, operation).get_position(
            id=data['idTransaction']
        )

        responseAlpaca = broker_alpaca_lib(api).close_position(
            id=data['idTransaction']
        )

        idTransaction = data['idTransaction']

        if responseAlpaca['status'] != 'accepted' and responseAlpaca['status'] != 'success':
            return {
                'status': 'error',
                'message': 'Not was possible to close the transaction in alpaca'
            }

        data = responseAlpacaPosition['data']

        # ALPACA PROFIT ----------------------------------------------------------------------------------------------------------------------
        basic_cost = data['cost_basis']
        profit_data = get_alpaca_percentage_profit_closed(api, idTransaction, basic_cost)

        trasactionLast.update(
            isClosed=True,
            price_closed=profit_data['close_price'],
            qty_close=profit_data['qty_close'],
            status='transactions_updated_calculate_profit'
        )

        results[operation]['transaction_closed'] = results[operation]['transaction_closed'] + 1
        # results[operation]['symbol'] = profit_data['symbol']
        # results[operation]['profit'] = profit_data['profit']
        # results[operation]['profit_percentage'] = profit_data['profit_percentage']

        return results
