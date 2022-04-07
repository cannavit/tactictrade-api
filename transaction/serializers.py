from email.policy import default
from rest_framework import serializers
from authentication.models import User
from strategy.models import strategyNews
from transaction.models import transactions
from authentication.models import User

from django.conf import settings
from transaction.models import transactions

from yahoo_fin import stock_info as si
from utils.brokers.broker_alpaca import broker_alpaca
from broker.models import alpaca_configuration, broker
import alpaca_trade_api as tradeapi

# Import datetime
from django.utils import timezone

class TransactionSelectSerializersGet(serializers.ModelSerializer):
            
    class Meta:
        model = transactions
        fields = "__all__"


    def to_representation(self, instance):
        
        response = super(TransactionSelectSerializersGet,
                         self).to_representation(instance)

        response['qty_open'] = round(response['qty_open'] ,1)
        response['qty_close'] = round(response['qty_close'] ,1)
        response['price_open'] = round(response['price_open'] ,1)
        response['price_closed'] = round(response['price_closed'] ,1)
        response['base_cost'] = round(response['base_cost'] ,1)
        response['close_cost'] = round(response['close_cost'] ,1)
        response['amount_open'] = round(response['amount_open'] ,1)
        response['amount_close'] = round(response['amount_close'] ,1)
        response['spread'] = round(response['spread'] ,4)
        response['profit'] = round(response['profit'] ,2)
        response['profit_percentage'] = round(response['profit_percentage'] ,3)
        response['create_at'] = response['create_at'][0:19]
        response['updated_at'] = response['updated_at'][0:19]


        return response
        
class TransactionSelectSerializersCreate(serializers.ModelSerializer):
                
    class Meta:

        model = transactions

        fields = [
            "owner",
            "strategyNews_id",
            "broker_id",
            "symbol_id",
            "is_paper_trading",
            "order",
            "operation",
            "qty_open",
            "price_open",
            "isClosed",
            "stop_loss",
            "take_profit",
            "base_cost",
            "idTransaction",
        ]




class TransactionSelectSerializers(serializers.ModelSerializer):

    class Meta:
        model = transactions

        fields = '__all__'

    def to_representation(self, instance):
        
        response = super(TransactionSelectSerializers,
                         self).to_representation(instance)


        
        profit_percentage = 0.0
        profit = 0.0
        price_open = 0.0
        current_price = 0.0

        price = si.get_live_price(instance.symbol.symbolName_corrected)

        if instance.broker.broker == 'alpaca':
            # Get Broker ID
            brokerId  = instance.broker.id
            alpacaBroker = alpaca_configuration.objects.get(broker_id=brokerId)
            api = tradeapi.REST(alpacaBroker.APIKeyID, alpacaBroker.SecretKey, alpacaBroker.endpoint)

            data = broker_alpaca(api, type=instance.operation).get_position(id=instance.idTransaction)
            
            if data['status'] == 'canceled':   
                # Edit the transaction to closed
                instance.closeType = 'canceled'
                instance.last_status = data['status']
                instance.isClosed = True
                instance.save()

            if instance.last_status != data['status']:
                instance.last_status = data['status']
                instance.save()

            if data['status'] == 'filled':

                # Get the delta time from now and updated_at
                deltaTime = timezone.now() - instance.updated_at
                deltaTime = deltaTime.total_seconds()
                dataAlpaca = data['data']
                instance.qty = dataAlpaca['qty']
                # cost_basis
                instance.base_cost= dataAlpaca['cost_basis']
                # profit
                instance.profit = dataAlpaca['profit_total']
                # profit_percentage
                instance.profit_percentage = dataAlpaca['profit_porcent']

                profit_percentage = instance.profit_percentage
                profit = instance.profit 

                if deltaTime > 60:
                    instance.save()
                
        if instance.operation == 'long' and instance.broker.broker != 'alpaca':
            profit = (price * instance.qty_open)  - (instance.price_open * instance.qty_open)
            current_price = (instance.price_open + profit) 
            profit_percentage = (current_price  - instance.price_open)/ instance.price_open
            profit_percentage = profit_percentage * 100
            
        
        elif instance.operation == 'short' and instance.broker.broker != 'alpaca':

            current_price =  instance.qty_open * price
            profit = instance.base_cost - current_price
            profit_percentage = (instance.base_cost - current_price)/ current_price
            profit_percentage = profit_percentage * 100


        if len(str(profit_percentage)) > 3 and instance.broker.broker != 'alpaca':
            profit_percentage = round(profit_percentage,0)
            profit = round(profit,0)
        else:
            profit_percentage = round(profit_percentage,1) 
            profit = round(profit,1)

        if len(str(current_price)) > 3 and instance.broker.broker != 'alpaca':
            current_price = round(current_price,1)
            price_open = round(response['price_open'],1)
        else:
            current_price = round(current_price,0)
            price_open =  round(response['price_open'],0) 



        response['profit_percentage'] = round(profit_percentage,3)
        response['profit'] = round(profit,2)
        response['current_price'] = round(price,1)
        response['price'] = round(price,1)
        response['symbol'] = instance.symbol.symbolName
        response['symbolUrl'] = instance.symbol.url
        response['broker'] = instance.broker.broker
        response['brokerName'] = instance.broker.brokerName
        response['isClose'] = instance.isClosed
        response['price_open'] = price_open
        response['base_cost'] = round(instance.base_cost,1)
        # number_stock
        response['number_stock'] = round(response['number_stock'],3)
        # stop_loss
        response['stop_loss'] = instance.stop_loss
        response['take_profit'] = instance.take_profit
        response['last_status'] = instance.last_status

        return response


#TODO Create Manual Close Transaction 

class closeTransactionSerializers(serializers.ModelSerializer):

    class Meta:
        model = transactions

        fields = '__all__'


