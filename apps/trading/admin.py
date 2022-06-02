from django import shortcuts
from django.contrib import admin
from django.forms import ValidationError

from apps.broker.brokers_connections.trading_control import broker_selector
from apps.trading.utils.trading_accions import trading_action
from .models import trading_config
from django.contrib import messages

from apps.transaction.models import transactions as transaction_model

from apps.strategy.models import strategyNews as strategy_model
# from .models import trading_parameters
# Register your models here.

# admin.site.register(trading_parameters)

results = {
            "long":  {
                "type": "buy",
                "transaction_opened": 0,
                "transaction_closed": 0,
                "follower_id_closed": [],
                "symbol": "",
                "follower_id_opened": [],
                "spread": 0,
                "qty": 0,
                "price_open": 0,
                "trade_type": 'long',
                "is_winner": False
            },
            "short": {
                "type": "buy",
                "transaction_opened": 0,
                "transaction_closed": 0,
                "symbol": "",
                "follower_id_closed": [],
                "follower_id_opened": [],
                "spread": 0,
                "qty": 0,
                "price_open": 0,
                "trade_type": 'short',
                "number_stocks": 0,
                "is_winner": False
            }
        }



@admin.action(description='Create Long Trade')
def create_long_order(modeladmin, request, queryset):

    for instance in queryset:
        #! Use only when is paper trading. 
        #? Note not use when is real trading.
        ## Close Open transaction
        if instance.is_paper_trading:
            try:
                message_success = trading_action(instance, order='buy')
                messages.success(request, message_success)
                # Close the open transaction if is opened.
            except Exception as e:
                messages.error(request, str(e))



@admin.action(description='Create Short Trade')
def create_short_order(modeladmin, request, queryset):

    for instance in queryset:

        #! Use only when is paper trading. 
        #? Note not use when is real trading.

        if instance.is_paper_trading:
            try:
                message_success = trading_action(instance, order='sell')
                messages.success(request, message_success)
                # Close the open transaction if is opened.
            except Exception as e:
                messages.error(request, str(e))
  






# Define Admin table view
class trading_config_admin(admin.ModelAdmin):

    list_display = [
        'id',
        'owner',
        'strategyNews',
        'broker',
        
        'is_paper_trading',
        'is_active_short',
        'is_active_long',
        'quantityUSDLong',
        'quantityQTYLong',
        'quantityUSDShort',
        'quantityQTYShort'      
    ]

    actions = [create_long_order, create_short_order]


admin.site.register(trading_config, trading_config_admin)
