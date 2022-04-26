from django.db import models
from apps.authentication.models import User


class symbolStrategy(models.Model):

    symbolName = models.CharField(
        blank=False, null=False, max_length=10, unique=True)

    symbolName_corrected = models.CharField(
        blank=True, null=True, max_length=10, unique=True)

    image = models.ImageField(upload_to='symbol/', null=True, blank=True)
    url = models.URLField(max_length=200, blank=True, null=True)

    is_crypto = models.BooleanField(default=False)

    def __str__(self):
        return self.symbolName


class strategyNews(models.Model):

    STRATEGY_PUSH = [
        ('https://s3.tradingview.com/userpics/6171439-Hlns_big.png', 'TradingView'),
    ]

    STRATEGY_TIME = [
        ('minutes', 'm'),
        ('hours', 'h'),
        ('days', 'd'),
        ('weeks', 'w'),
    ]

    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='maintainer')
    strategyNews = models.CharField(blank=False, max_length=60, unique=False)

    symbol = models.ForeignKey(
        to=symbolStrategy, on_delete=models.CASCADE, blank=True, null=False)

    pusher = models.CharField(
        choices=STRATEGY_PUSH, default='tradingview', null=True, blank=True, max_length=60)

    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # ? User manual stadistic strategy
    net_profit = models.FloatField(default=0, null=False, blank=False)
    percentage_profitable = models.FloatField(
        default=0, null=False, blank=False)

    max_drawdown = models.FloatField(default=0, null=False, blank=False)
    profit_factor = models.FloatField(default=0, null=False, blank=False)

    # ? Automatic stadistic strategy
    is_verified = models.BooleanField(default=False)
    net_profit_verified = models.FloatField(default=0, null=True, blank=True)
    percentage_profitable_verified = models.FloatField(
        default=0, null=True, blank=True)

    # ? Community values
    ranking = models.IntegerField(default=0, null=True, blank=True)

    strategy_link = models.CharField(
        blank=True, null=True, max_length=400, default="")
    strategy_token = models.CharField(
        blank=True, null=True, max_length=400, unique=True)

    period = models.CharField(
        choices=STRATEGY_TIME, null=True, blank=True, max_length=60, default='hours')
        
    timer = models.IntegerField(default=1, null=True, blank=True)

    description = models.TextField(max_length=600, null=True, blank=True)
    post_image = models.ImageField(upload_to='strategy_post_image', blank=True)

    # Define Url Image
    url_image = models.URLField(blank=True, null=True, default='')

    likes = models.ManyToManyField(User, blank=True)
    
    favorite = models.ManyToManyField(
        User, related_name='favorite', blank=True)

    follower = models.ManyToManyField(
        User, related_name='follower', blank=True)

    email_bot = models.CharField(
        blank=True, null=True, max_length=60, default="")

    def __str__(self):
        return self.strategyNews

    # def check_name_if_exist_this_strategy(self):
    #     if self.__class__.object.filter(strategyNews=self.strategyNews):
    #         return False
    #     else:
    #         return True

# eturned non-string (type
