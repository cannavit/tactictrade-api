from django.db import models
from apps.authentication.models import User
from apps.strategy.models import strategyNews
from apps.broker.models import broker
# Create your models here.
from django.db.models.signals import  pre_save
from django.dispatch import receiver

class trading_config(models.Model):

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    strategyNews = models.ForeignKey(to=strategyNews, on_delete=models.CASCADE)
    broker = models.ForeignKey(to=broker, on_delete=models.CASCADE)

    # Trading Long Parameters: 
    quantityUSDLong = models.FloatField(default=0, blank=True,null=True)
    quantityQTYLong = models.FloatField(default=0, blank=True,null=True)

    useLong =  models.BooleanField(default=False, blank=True,null=True)
    stopLossLong = models.FloatField( null=True, blank=True, default=-3)
    stopLossLongUsd = models.FloatField( null=True, blank=True, default=-3)

    takeProfitLong = models.FloatField( null=True, blank=True, default=10)
    takeProfitLongUsd = models.FloatField( null=True, blank=True, default=10)
    consecutiveLossesLong = models.IntegerField( null=True, blank=True, default=3)
    
    # Trading Short Parameters:
    quantityUSDShort = models.FloatField(default=0, blank=True,null=True)
    quantityQTYShort = models.FloatField(default=0, blank=True,null=True)

    useShort =  models.BooleanField(default=False, blank=True,null=True)
    stopLossShort = models.FloatField( null=True, blank=True, default=-3)
    takeProfitShort = models.FloatField( null=True, blank=True, default=10)
    consecutiveLossesShort = models.IntegerField( null=True, blank=True, default=3)

    # Reference Data
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Init Parameters
    initialCapitalUSDLong = models.FloatField(default=0, blank=True,null=True)
    initialCapitalUSDShort = models.FloatField(default=0, blank=True,null=True)
    
    initialCapitalQTYLong = models.FloatField(default=0, blank=True,null=True)
    initialCapitalQTYShort = models.FloatField(default=0, blank=True,null=True)

    initialQuantityLong = models.FloatField(default=0, blank=True,null=True)
    initialQuantityShort = models.FloatField(default=0, blank=True,null=True)

    winTradeLong = models.IntegerField(default=0, blank=True,null=True)
    winTradeShort = models.IntegerField(default=0, blank=True,null=True)
    closedTradeShort = models.IntegerField(default=0, blank=True,null=True)
    closedTradeLong = models.IntegerField(default=0, blank=True,null=True)
    profitPorcentageShort = models.FloatField(default=0, blank=True,null=True)
    profitPorcentageLong = models.FloatField(default=0, blank=True,null=True)

    # Control data
    is_active = models.BooleanField(default=False, blank=True,null=True)
    is_active_short = models.BooleanField(default=False, blank=True,null=True)
    is_active_long = models.BooleanField(default=False, blank=True,null=True)
    close_trade_long_and_deactivate = models.BooleanField(default=False, blank=True,null=True)
    close_trade_short_and_deactivate = models.BooleanField(default=False, blank=True,null=True)
    is_paper_trading = models.BooleanField(default=True, blank=True,null=True)

    # Stadistics Trading Long:
    numberOfTradesLong = models.IntegerField(default=0, blank=True,null=True)
    numberOfWindTradeLong = models.IntegerField(default=0, blank=True,null=True)
    currentLongUSDvalue = models.FloatField(default=0, blank=True,null=True)
    percentageProfitLong = models.FloatField(default=0, blank=True,null=True)

    # Stadistics Trading Short:
    numberOfTradesShort = models.IntegerField(default=0,blank=True,null=True)
    numberOfWindTradeShort = models.IntegerField(default=0,blank=True,null=True)
    currentShortUSDvalue = models.FloatField(default=0,blank=True,null=True)
    percentageProfitShort = models.FloatField(default=0,blank=True,null=True)

    def __str__(self):
        return self.owner.email



class strategy(models.Model):

    strategy = models.CharField(
        max_length=255, blank=False, null=False, unique=False)
    order = models.CharField(max_length=255, blank=True, null=True)
    contracts = models.CharField(max_length=255, blank=True, null=True)
    ticker = models.CharField(max_length=255, blank=True, null=True)
    position_size = models.CharField(max_length=255, blank=True, null=True)
    bot_token = models.CharField(
        max_length=255, blank=False, null=False, unique=False)

    def __str__(self):
        return self.strategy


@receiver(pre_save, sender=trading_config)
def pre(sender, instance, *args, **kwargs):

    if instance.id is None:
        
        instance.initialCapitalUSDLong = instance.quantityUSDLong
        instance.initialCapitalUSDShort = instance.quantityUSDShort
        instance.initialCapitalQTYLong = instance.quantityQTYLong
        instance.initialCapitalQTYShort = instance.quantityQTYShort
        instance.winTradeLong = 0
        instance.winTradeShort = 0
        instance.closedTradeShort = 0
        instance.closedTradeLong = 0
        instance.profitPorcentageShort = 0
        instance.profitPorcentageLong = 0

