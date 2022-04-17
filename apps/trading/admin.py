from django.contrib import admin

from apps.broker.brokers_connections.trading_control import broker_selector
from .models import trading_config
from django.contrib import messages


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

        tradingConfig = trading_config.objects.get(
            owner_id=instance.owner_id, strategyNews_id=instance.strategyNews_id)

        # Create Long Trade From Admin.

        broker_selector(
            trading_config=tradingConfig,
            strategyNewsId=instance.strategyNews_id,
            follower_id=instance.owner_id,
            strategyData=instance.strategyNews
        ).long_trade(
            order='buy',
            broker_name=instance.broker.broker,
            is_active_long=tradingConfig.is_active_long,
            results=results,
        )

        messages.success(request, 'Long Trade Created')

@admin.action(description='Create Short Trade')
def create_short_order(modeladmin, request, queryset):

    for instance in queryset:

        tradingConfig = trading_config.objects.get(
            owner_id=instance.owner_id, strategyNews_id=instance.strategyNews_id)

        # Create Long Trade From Admin.

        broker_selector(
            trading_config=tradingConfig,
            strategyNewsId=instance.strategyNews_id,
            follower_id=instance.owner_id,
            strategyData=instance.strategyNews
        ).short_trade(
            order='sell',
            broker_name=instance.broker.broker,
            is_active_short=tradingConfig.is_active_short,
            results=results,
        )

        messages.success(request, 'Long Trade Created')



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
