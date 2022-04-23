from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.authentication.models import User
from apps.strategy.models import symbolStrategy


class broker(models.Model):

    BROKER_OPTIONS = [
        ('alpaca', 'Alpaca'),
        ('paperTrade', 'paperTrade'),
    ]

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    capital = models.FloatField(default=0, blank=False, null=False)
    isPaperTrading = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    broker = models.CharField(choices=BROKER_OPTIONS, max_length=255, blank=False,
                              null=False, unique=False, default='paperTrade')
    tagBroker = models.CharField(
        max_length=20, blank=True, null=False, default='')
    tagPrice = models.CharField(
        max_length=20, blank=True, null=False, default='')
    isActive = models.BooleanField(default=True)
    block_is_active = models.BooleanField(default=False)
    brokerName = models.CharField(
        max_length=255, blank=False, null=False, unique=False, default='Zipi Paper Trade')
    urlLogo = models.CharField(
        max_length=255, blank=False, null=False, unique=False, default='')

    short_is_allowed = models.BooleanField(default=True)
    short_allowed_fractional = models.BooleanField(default=True)

    long_is_allowed = models.BooleanField(default=True)
    long_allowed_fractional = models.BooleanField(default=True)

    short_is_allowed_crypto = models.BooleanField(default=True)
    short_allowed_fractional_crypto = models.BooleanField(default=True)

    long_is_allowed_crypto = models.BooleanField(default=True)
    long_allowed_fractional_crypto = models.BooleanField(default=True)

    def __str__(self):
        return self.brokerName


@receiver(pre_save, sender=broker)
def pre_save_profit(sender, instance, *args, **kwargs):

    if instance.broker == 'paperTrade':

        instance.short_is_allowed = True
        instance.short_allowed_fractional = True
        instance.long_is_allowed = True
        instance.long_allowed_fractional = True
        instance.short_is_allowed_crypto = True
        instance.short_allowed_fractional_crypto = True
        instance.long_is_allowed_crypto = True
        instance.long_allowed_fractional_crypto = True

    elif instance.broker == 'alpaca':

        instance.long_is_allowed = True
        instance.short_is_allowed = True
        
        instance.short_allowed_fractional = False 
        instance.long_allowed_fractional = True

        instance.short_is_allowed_crypto = False
        instance.long_is_allowed_crypto = True
                
        instance.short_allowed_fractional_crypto = False
        instance.long_allowed_fractional_crypto = True


class alpaca_configuration(models.Model):

    TRADING_OPTIONS = [

        ('https://paper-api.alpaca.markets', 'https://paper-api.alpaca.markets'),
        ('Add URL by Production URL', 'Add URL by Production URL'),
    ]


    broker = models.ForeignKey(to=broker, on_delete=models.CASCADE)

    APIKeyID = models.CharField(
        max_length=255, blank=False, null=False, unique=False)

    SecretKey = models.CharField(
        max_length=255, blank=False, null=False, unique=False)

    endpoint = models.CharField(choices=TRADING_OPTIONS, max_length=255, blank=False,
                                null=False, unique=False, default='https://paper-api.alpaca.markets')

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    # return self.broker.ownerp
