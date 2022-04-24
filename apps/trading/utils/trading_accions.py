from django import shortcuts
from django.contrib import admin
from django.forms import ValidationError

from apps.broker.brokers_connections.trading_control import broker_selector

from apps.transaction.models import transactions as transaction_model

from apps.strategy.models import strategyNews as strategy_model
# from .models import trading_parameters
# Register your models here.
#* instance: is trading_config



def trading_action(instance, order='sell'):
    
    if order == 'buy' or order == 'sell':
        success_message = ""
        #! Close old short        
        #! Open New Trade [OPEN-OPERATIONS-LONG-BUY]
        # Open a new trade
        try:

            response = transaction_model.objects.create(
                owner_id=instance.owner_id,
                strategyNews_id=instance.strategyNews_id,
                broker_id=instance.broker_id,
                symbol_id=instance.strategyNews.symbol.id,
                trading_config_id=instance.id,
                order=order
            )

            success_message = 'Success Open Trade ' + order + ' ' + str(response.id)

            return success_message

        except Exception as e:
            raise ValidationError(str(e))
