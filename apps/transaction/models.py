# Create your models here.
# from re import I
from django.db import models
# Create your models here.
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from utils.brokers.broker_alpaca import broker_alpaca_lib
from utils.calculate_porcentaje import pct_change
from yahoo_fin import stock_info as si

from apps.authentication.models import User
from apps.broker.models import broker, alpaca_configuration
from apps.strategy.models import strategyNews, symbolStrategy
from apps.trading.models import trading_config
from apps.setting.models import setting as setting_model

from django.core.exceptions import ValidationError

import alpaca_trade_api as tradeapi
# import message library
from django.contrib import messages

from utils.convert_json_to_objects import convertJsonToObject

from apps.notification.models import notification as notification_model
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



# Check if exist one open transaction
def break_if_exist_open_transaction(instance):

    close_transaction = False
    # Check if exist one transaction open
    transactions_obj = transactions.objects.filter(
         owner_id=instance.owner_id,
         strategyNews_id=instance.strategyNews_id,
         broker_id=instance.broker_id,
         symbol_id=instance.strategyNews.symbol.id,
         isClosed__in=[False],
     ).order_by('-id')
    
    exist = transactions_obj.exists()

    if not exist:
        close_transaction = False
        return convertJsonToObject({
            'close_transaction': close_transaction,
            'transactions_obj': {}
        })

    instance_old = transactions_obj.first()

    if instance_old.order == instance.order:
        raise ValidationError("Exist one operation is Opened")
    else:
        # In this case exist one transaction open with the !order
        close_transaction = True

    results =  convertJsonToObject(
        {
        'close_transaction': close_transaction,
      
        }
    )

    results.instance_old =  instance_old

    return results



# Open The connection with alpaca broker    
def open_alpaca_connection(instance=None):

    if instance.trading_config.is_active_long or instance.trading_config.is_active_short:
        
        alpaca_configuration_obj = alpaca_configuration.objects.get(broker_id=instance.broker.id)
        try:
            api = tradeapi.REST(
                key_id=alpaca_configuration_obj.APIKeyID,
                secret_key=alpaca_configuration_obj.SecretKey,
                base_url='https://paper-api.alpaca.markets'
                )
            return api
        except Exception as e:
            raise ValidationError("Error Broker Api connection: " + str(e))

    else:
        raise ValidationError("Not active long or short")
        
@receiver(pre_save, sender=transactions)
def pre_save_profit(sender, instance, *args, **kwargs):

    # Get Price of stock buy or sell
    try:
        price = si.get_live_price(instance.symbol.symbolName_corrected)
    except Exception as e:
        
        raise ValidationError("Not detected stock in yahoo_fin CM1232A " + instance.symbol.symbolName_corrected)

    #! CREATED TRANSACTION
    if instance.id is None:
        # Fail of exist one open transaction
        """
         Check if exist one transaction open with the same order='buy' or 'sell'
         If exist one last transaction with the same order the next function go to break 
         the code.
                                                                                """ 
        transaction_last_obj = break_if_exist_open_transaction(instance)



        #! [CLOSE OLD TRANSACTION] --------------------------------------
        #! ---------------------------------------------------------------
        #! ---------------------------------------------------------------

        """
            Close the last transactions
                order -> sell or order -> buy
        """
        if transaction_last_obj.close_transaction:

            instance_old = transaction_last_obj.instance_old
            instance_old.price_closed = price
            # Close the open transaction.  
            if instance.broker.broker == 'paperTrade':
                # Close open trade Long Trade
                if instance_old.order == 'buy':
                    send_notification = True

                    instance_old.price_closed = price
                    instance_old.qty_close = (instance_old.qty_open * instance_old.price_open)/ instance_old.price_closed
                    instance_old.close_cost = instance_old.qty_close * instance_old.price_closed    
                    instance_old.profit   = instance_old.close_cost - instance_old.base_cost   

                    instance_old.profit_percentage = pct_change(
                        float(instance_old.base_cost), float(instance_old.close_cost))

                    if instance_old.profit > 0:
                        instance_old.is_winner = True

                    instance_old.isClosed = True
                    instance_old.save()


                if instance_old.order == 'sell':
                    
                    instance_old.qty_close = (instance_old.qty_open * instance_old.price_open)/ instance_old.price_closed
                    instance_old.profit = instance_old.base_cost - instance_old.qty_close *  instance_old.price_closed
                    instance_old.profit_percentage = (instance_old.price_closed* instance_old.qty_close - instance_old.base_cost)/ instance_old.base_cost

                    instance_old.close_cost = instance_old.qty_close * instance_old.price_closed    
                    instance_old.profit   = instance_old.close_cost - instance_old.base_cost    

                    instance_old.profit_percentage = pct_change(
                        float(instance_old.base_cost), float(instance_old.close_cost))

                    if instance_old.profit > 0:
                        instance_old.is_winner = True

                    instance_old.isClosed = True
                    instance_old.save()


            if instance_old.broker.broker == 'alpaca':
            # Get api alpaca connection
                api = open_alpaca_connection(instance)
                try:

                    broker_results = broker_alpaca_lib(api,
                        symbol=instance_old.symbol.symbolName,
                        price=price).close_position(id=instance_old.idTransaction)

                    instance_old.qty_close = float(broker_results.response.qty)
                    # instance_old.price_closed = float(broker_results.response.price)
                    instance_old.status = 'accepted_alpaca'

                    if instance_old.profit > 0:
                        instance_old.is_winner = True

                    instance_old.isClosed = True
                    instance_old.save()

                except Exception as e:
                    raise ValidationError(str(e.message))

                    
        #? [OPEN NEW TRANSACTION] --------------------------------------
        #? ---------------------------------------------------------------
        #? ---------------------------------------------------------------
        # Login for paper trading
       

        #? PAPERTRADING ------------------------------------------------------------------------
        if instance.broker.broker == 'paperTrade':
            instance.price_open = price
            

            # instance.take_profit = instance.trading_config.take_profit
            # instance.stop_loss = instance.trading_config.stop_loss

            if instance.order == 'buy' and instance.trading_config.is_active_long:

                spread_procentage = 0.000185
                spread = price * spread_procentage
                # Calculate spread
                original_price = price
                price = price + spread

                instance.base_cost = instance.trading_config.initialCapitalUSDLong
                # Calculate qty bt paperTrade
                qty = (instance.trading_config.initialCapitalUSDLong - spread) / price
                # 1000 - 
                instance.qty_open = qty
                instance.price_open = original_price



            elif instance.order == 'sell' and instance.trading_config.is_active_short:

                spread_procentage = 0.000185
                spread = price * spread_procentage

                # Calculate spread
                original_price = price
                price = price - spread

                instance.base_cost = instance.trading_config.initialCapitalUSDShort

                qty = (instance.trading_config.initialCapitalUSDShort + spread) / price

                instance.qty_open = qty
                instance.price_open = original_price


        #? ALPACA [BUY] ------------------------------------------------------------------------
        if instance.broker.broker == 'alpaca':
            instance.price_open = price
            # Init Alpaca configuration for create trade
            api = open_alpaca_connection(instance)
        
            if instance.order == 'buy' and instance.trading_config.is_active_long:
                instance.base_cost = instance.trading_config.initialCapitalUSDLong

                #? Close Short old operations. 
                try:
                    
                    #! Open Long Trade [BUY] with Alpaca
                    alpaca_transaction_response = broker_alpaca_lib(api,
                        symbol=instance.symbol.symbolName,
                        price=price).long_buy(
                        qty=instance.trading_config.quantityQTYLong,
                        notional=instance.trading_config.quantityUSDLong,
                        stop_loss_porcent=instance.trading_config.stopLossLong,
                        take_profit_porcent=instance.trading_config.takeProfitLong,
                        broker=instance.trading_config.broker,
                    )

                    instance.idTransaction = alpaca_transaction_response.data.id
                    instance.take_profit = alpaca_transaction_response.data.take_profit
                    instance.stop_loss = alpaca_transaction_response.data.stop_loss

                    print(alpaca_transaction_response)

                except Exception as e:
                    raise ValidationError(str(e.message))

            elif instance.order == 'sell' and instance.trading_config.is_active_short:

                #! Open Long Trade [BUY] with Alpaca

                try:

                    alpaca_transaction_response = broker_alpaca_lib(api,
                        symbol=instance.symbol.symbolName,
                        price=price).short_buy(
                        qty=instance.trading_config.quantityQTYShort,
                        notional=instance.trading_config.quantityUSDShort,
                        stop_loss_porcent=instance.trading_config.stopLossShort,
                        take_profit_porcent=instance.trading_config.takeProfitShort,
                    )

                    instance.idTransaction = alpaca_transaction_response.data.id
                    instance.take_profit = alpaca_transaction_response.data.take_profit
                    instance.stop_loss = alpaca_transaction_response.data.stop_loss

                except Exception as e:
                    raise ValidationError(str(e.message))



"""
     Send notification after to save the transaction data inside to the DB
"""
@receiver(post_save, sender=transactions)
def pre_save_profit(sender, instance, *args, **kwargs):

    if instance.order == 'buy' and instance.trading_config.is_active_long:

        setting_active = setting_model.objects.get(owner_id=instance.owner.id,setting='Receive Long Notifications Push')

        print(setting_active)
        
        instance.operation = 'long'

        if setting_active.bool_value:

            notification_model.objects.create(
                owner_id=instance.owner_id,
                transact_id=instance.id,
                notification='open_long_buy',
                is_trade=True,
                isClosed=False,
                symbol=instance.symbol.symbolName,
                image=instance.symbol.url,
                strategyName=instance.strategyNews.strategyNews,
                base_cost=instance.base_cost,
                base_price=instance.price_open,
                order=instance.order,
                operation=instance.operation,
                
            )

    if instance.order == 'sell' and instance.trading_config.is_active_short:

        instance.operation = 'short'

        setting_active_short = setting_model.objects.get(owner_id=instance.owner.id,setting='Receive Short Notifications Push')

        if setting_active_short.bool_value:

            notification_model.objects.create(
                owner_id=instance.owner_id,
                transact_id=instance.id,
                notification='close_long_sell',
                is_trade=True,
                isClosed=False,
                symbol=instance.symbol.symbolName,
                image=instance.symbol.url,
                strategyName=instance.strategyNews.strategyNews,
                base_cost=instance.base_cost,
                base_price=instance.price_open,
                order=instance.order,
                operation=instance.operation,
                profit=instance.profit,
            )