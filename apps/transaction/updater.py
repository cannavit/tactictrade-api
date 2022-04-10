
from datetime import datetime

import alpaca_trade_api as tradeapi
from apscheduler.schedulers.background import BackgroundScheduler
# import django settings
from django.conf import settings
from utils.brokers.broker_alpaca import broker_alpaca_lib
from utils.calculate_porcentaje import pct_change
from yahoo_fin import stock_info as si

from apps.broker.models import alpaca_configuration, broker
from apps.strategy.models import symbolStrategy
from apps.transaction.models import transactions


def update_accepted_broker_transactions():

    # Get transactions with status='accepted'
    transactions_accepted = transactions.objects.filter(status='accepted_alpaca')
    print('---- ---- ---- RUN SCHEDULER accepted_alpaca task')

    if transactions_accepted.count() > 0:
        print('Exist Transactions Opened')

        for transactions_i in transactions_accepted.values():
            broker_selected = broker.objects.get(id=transactions_i['broker_id'])
            alpaca = alpaca_configuration.objects.get(broker=broker_selected)

            api = tradeapi.REST(alpaca.APIKeyID, alpaca.SecretKey, alpaca.endpoint)

            transaction_id = transactions_i['idTransaction']

            position_opened = api.list_orders(status='opened', limit=100, nested=True)

            for position in position_opened:
                
                if position.id == transaction_id or position.client_order_id == transaction_id:
                    
                    amount_open = float(position.filled_avg_price) * float(position.filled_qty)
                    spread = float(transactions_i['base_cost']) - amount_open

                    transactions_accepted.filter(id=transactions_i['id']).update(
                        status='closed',
                        qty_open=float(position.filled_qty),
                        price_open=float(position.filled_avg_price),
                        amount_open=amount_open,
                        spread=spread
                    )
                        

                    print('---- ---- ----[UPDATED] RUN SCHEDULER accepted_alpaca task')

def scheduler_transactions_updated_calculate_profit():

    transactions_job = transactions.objects.filter(status='transactions_updated_calculate_profit')

    print(' [schaduler job] transactions_updated_calculate_profit ')

    if transactions_job.count() > 0:

        for transactions_i in transactions_job.values():


            broker_selected = broker.objects.get(id=transactions_i['broker_id'])

            brokerName = broker_selected.broker

            if brokerName == 'paperTrade':
                # symbol_id 
                symbol_obj = symbolStrategy.objects.get(id=transactions_i['symbol_id'])
                price_closed = si.get_live_price(symbol_obj.symbolName_corrected)
                transactions_i['price_closed'] = price_closed
                print('---- ---- ----[UPDATED] RUN SCHEDULER transactions_updated_calculate_profit task')

                # close_cost

            close_cost = transactions_i['qty_close'] * transactions_i['price_closed']
            profit =   close_cost - transactions_i['base_cost']
                
            profit_percentage = pct_change(
                float(transactions_i['base_cost']), float(close_cost))

            transactions_job.filter(id=transactions_i['id']).update(
                        status='closed',
                        close_cost=close_cost,
                        price_closed=transactions_i['price_closed'],
                        profit=profit,
                        profit_percentage=profit_percentage,
                        amount_close=close_cost,
                        )


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_accepted_broker_transactions, 'interval', seconds=30)
    scheduler.add_job(scheduler_transactions_updated_calculate_profit, 'interval', seconds=30)
    scheduler.start()
