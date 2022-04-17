# Create your models here.
from django.db import models
# Create your models here.
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from utils.calculate_porcentaje import pct_change
from yahoo_fin import stock_info as si

from apps.authentication.models import User
from apps.broker.models import broker
from apps.strategy.models import strategyNews, symbolStrategy
from apps.trading.models import trading_config



class transactions(models.Model):

    ORDER_TYPE = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    OPERATION_TYPE = [
        ('long', 'Long'),
        ('short', 'Short'),
    ]

    CLOSED_TRADE_TYPE = [
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('canceled', 'Canceled'),
        ('accepted', 'Accepted'),
    ]

    STATUS_OF_TRANSACTION = [
        ('opened', 'opened'),
        ('success', 'success'),
        ('close', 'close'),
        ('pending', 'pending'),
        ('error', 'error'),
        ('close_pending', 'close_pending'),
        ('accepted_alpaca', 'accepted_alpaca'),
        ('transactions_updated_calculate_profit', 'transactions_updated_calculate_profit')
    ]

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE,null=False)
    strategyNews = models.ForeignKey(to=strategyNews, on_delete=models.CASCADE,null=False)
    broker = models.ForeignKey(to=broker, on_delete=models.CASCADE,null=False)
    trading_config = models.ForeignKey(to=trading_config, on_delete=models.CASCADE,null=False)
    symbol = models.ForeignKey(to=symbolStrategy, on_delete=models.CASCADE, null=False)

    is_paper_trading = models.BooleanField(default=True, blank=True,null=True)

    order = models.CharField(choices=ORDER_TYPE, max_length=255, blank=False,
                                null=False, unique=False, default='sell')    

    operation = models.CharField(choices=OPERATION_TYPE, max_length=255, blank=False, default='long')

    # Quatity of stock buy or sell
    qty_open = models.FloatField(default=0, blank=True,null=True)
    qty_close = models.FloatField(default=0, blank=True,null=True)

    # Price of stock buy or sell
    price_open = models.FloatField(default=0, blank=True,null=True)
    price_closed = models.FloatField(default=0, blank=True,null=True)

    # Cost of buy the action
    base_cost = models.FloatField(default=0, blank=True,null=True)
    close_cost = models.FloatField(default=0, blank=True,null=True)

    # This is the real value of the action
    amount_open = models.FloatField(default=0, blank=True,null=True)
    amount_close = models.FloatField(default=0, blank=True,null=True)

    # spread of the action
    spread = models.FloatField(default=0, blank=True,null=True)
    # STATUS_OF_TRANSACTION
    status = models.CharField(choices=STATUS_OF_TRANSACTION, max_length=255, blank=False, default='closed')

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    isClosed = models.BooleanField(default=False, blank=False, null=False)

    stop_loss = models.FloatField(default=-1, blank=True,null=True)
    stop_loss_qty = models.FloatField(default=-1, blank=True,null=True)

    take_profit = models.FloatField(default=-1, blank=True,null=True)
    take_profit_qty = models.FloatField(default=-1, blank=True,null=True)

    is_winner = models.BooleanField(default=False)

    broker_transaction_id = models.CharField(max_length=255, blank=True,null=True)
    
    number_stock =  models.FloatField(default=0, blank=True,null=True)

    closeType = models.CharField(choices=CLOSED_TRADE_TYPE, max_length=255, blank=False, default='automatic')

    # Text field
    idTransaction = models.CharField(max_length=255, blank=True,null=True)

    last_status = models.CharField(max_length=255, blank=True,null=True, default='')

    # Profit 
    profit = models.FloatField(default=0, blank=True,null=True)
    profit_percentage = models.FloatField(default=0, blank=True,null=True)


@receiver(pre_save, sender=transactions)
def pre_save_profit(sender, instance, *args, **kwargs):

    if instance.broker.broker == 'paperTrade':
        symbol = instance.strategyNews.symbol.symbolName_corrected
        price = si.get_live_price(symbol)

    #TODO create logic for buy using qty 
    trading_config = instance.trading_config

    print(trading_config)

    # CREATED TRANSACTION
    if instance.id is None:


        if instance.broker.broker == 'paperTrade':

            if instance.operation == 'long':

                spread_procentage = 0.000185

                spread = price * spread_procentage
                original_price = price

                price = price + spread
                qty = (instance.base_cost - spread) /price

                instance.qty_open = qty

                instance.price_open = original_price
                instance.qty_close = qty

            elif instance.operation == 'short':
                print('This is one short')

    # UPDATED TRANSACTION
    else:

        if instance.operation == 'long':

            if instance.broker.broker == 'paperTrade':
                instance.price_closed = price

            instance.close_cost = instance.qty_close * instance.price_closed    
            instance.profit   = instance.close_cost - instance.base_cost      

            instance.profit_percentage = pct_change(
                float(instance.base_cost), float(instance.close_cost))
            
            instance.status = 'closed'
            instance.isClosed = True



