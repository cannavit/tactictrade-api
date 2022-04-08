from asyncore import read
from urllib import response
from aiohttp import request
from rest_framework import serializers

# Import Utils models
from apps.trading.models import trading_config, strategy
from apps.strategy.models import strategyNews
from apps.authentication.models import User
from apps.broker.models import broker
from apps.transaction.models import transactions
from django.db.models import Sum


class tradingConfigSerializerPut(serializers.ModelSerializer):

    # Bool params not required
    is_active_short = serializers.BooleanField(required=False)
    is_active_long = serializers.BooleanField(required=False)
    quantityUSDLong = serializers.FloatField(required=False)
    useLong = serializers.BooleanField(required=False)
    stopLossLong = serializers.FloatField(required=False)
    takeProfitLong = serializers.FloatField(required=False)
    consecutiveLossesLong = serializers.IntegerField(required=False)
    quantityUSDShort = serializers.FloatField(required=False)
    useShort = serializers.BooleanField(required=False)
    stopLossShort = serializers.FloatField(required=False)
    takeProfitShort = serializers.FloatField(required=False)
    consecutiveLossesShort = serializers.IntegerField(required=False)

    is_active = serializers.BooleanField(required=False)
    close_trade_long_and_deactivate = serializers.BooleanField(required=False)
    close_trade_short_and_deactivate = serializers.BooleanField(required=False)


    class Meta:
        model = trading_config
        # not mandatory fields declaration
        fields = [
            'is_active_short',
            'is_active_long',
            'quantityUSDLong',
            'useLong',
            'stopLossLong',
            'takeProfitLong',
            'consecutiveLossesLong',
            'quantityUSDShort',
            'useShort',
            'stopLossShort',
            'takeProfitShort',
            'consecutiveLossesShort',
            'is_active',
            'close_trade_long_and_deactivate',
            'close_trade_short_and_deactivate',
        ]

       
class tradingConfigSerializers(serializers.ModelSerializer):

    # Declarate the next serializer to use
    owner = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=User.objects.all())
    strategyNews = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=strategyNews.objects.all())
    broker = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=broker.objects.all())
        
    quantityUSDLong = serializers.FloatField(default=-1)
    useLong = serializers.BooleanField(default=True)
    stopLossLong = serializers.FloatField(default=-1)
    takeProfitLong = serializers.FloatField(default=-1)
    consecutiveLossesLong = serializers.IntegerField(default=-1)
    quantityUSDShort = serializers.FloatField(default=-1)
    useShort = serializers.BooleanField(default=False)
    stopLossShort = serializers.FloatField(default=-1)
    takeProfitShort = serializers.FloatField(default=-1)
    consecutiveLossesShort = serializers.IntegerField(default=-1)
    is_active = serializers.BooleanField(default=True)
    is_active_short = serializers.BooleanField(default=True)
    is_active_long = serializers.BooleanField(default=True)
    close_trade_long_and_deactivate = serializers.BooleanField(default=False)
    close_trade_short_and_deactivate = serializers.BooleanField(default=False)
    initialCapitalUSDLong = serializers.FloatField(default=0)
    initialCapitalUSDShort = serializers.FloatField(default=0)
    winTradeLong = serializers.FloatField(default=0)
    winTradeShort = serializers.FloatField(default=0)
    closedTradeShort = serializers.FloatField(default=0)
    closedTradeLong = serializers.FloatField(default=0)
    profitPorcentageShort = serializers.FloatField(default=0)
    profitPorcentageLong = serializers.FloatField(default=0)

    class Meta:

        model = trading_config

        fields = [
            'owner',
            'strategyNews',
            'broker',
            'quantityUSDLong',
            'useLong',
            'stopLossLong',
            'takeProfitLong',
            'consecutiveLossesLong',
            'quantityUSDShort',
            'useShort',
            'stopLossShort',
            'takeProfitShort',
            'consecutiveLossesShort',
            'is_active',
            'is_active_short',
            'is_active_long',
            'close_trade_long_and_deactivate',
            'close_trade_short_and_deactivate',
            'initialCapitalUSDLong',
            'initialCapitalUSDShort',
            'winTradeLong',
            'winTradeShort',
            'closedTradeShort',
            'closedTradeLong',
            'profitPorcentageShort',
            'profitPorcentageLong',
        ]

    def to_representation(self, instance):


        transactionsData = transactions.objects.filter(
                        owner_id=instance.owner.id,
                        symbol=instance.strategyNews.symbol,
                        isClosed__in=[True],
                        strategyNews_id=instance.strategyNews.id,
            )

        
        transactionsDataLong = transactionsData.filter(
                          operation="long",
                          is_winner__in=[True]

        )

        transactionsDataShort = transactionsData.filter(
                        operation="short",
                        is_winner__in=[True]
            )

        transactionsDataTotalShort = transactionsData.filter(
                operation="short",
        )
        
        transactionsDataTotalLong = transactionsData.filter(
                operation="long",
        )

        # Count data

        transactionsDataLongCount  = transactionsDataLong.count()
        transactionsDataShortCount = transactionsDataShort.count()        
        transactionsDataTotalLongCount = transactionsDataTotalLong.count()
        transactionsDataTotalShortCount = transactionsDataTotalShort.count()


        # Get Total Profit


        #? ------------------------------------------------------------ 

        response = super(tradingConfigSerializers,
                         self).to_representation(instance)

        response['strategyNews_id'] = instance.strategyNews.id
        # Get the strategyNews name
        response['strategyNews_name'] = instance.strategyNews.strategyNews
        response['strategyNews_pusher'] = instance.strategyNews.pusher
        response['symbol_url'] = instance.strategyNews.symbol.url
        response['symbol_name'] = instance.strategyNews.symbol.symbolName

        response['symbol_symbolName'] = instance.strategyNews.symbol.symbolName

        response['symbol_time'] = str(
            instance.strategyNews.timer) + instance.strategyNews.period[0:1]

        response['broker_name'] = instance.broker.broker.title()
        
        response['broker_brokerName'] = instance.broker.brokerName.title()

        response['totalNumberOfWinTrades'] = transactionsDataLongCount + transactionsDataShortCount

        transactionsDataPrifitData = transactionsData.aggregate(Sum('profit_percentage'))
        if transactionsDataPrifitData['profit_percentage__sum'] is None:
            transactionsDataPrifitData['profit_percentage__sum']  = 0.0

        response['totalTradingProfit'] = round(transactionsDataPrifitData['profit_percentage__sum'],1)

        response['totalOfTrades'] = transactionsDataTotalLongCount + transactionsDataTotalShortCount

        totalProfitUSDSum = transactionsData.aggregate(Sum('profit'))
        if totalProfitUSDSum['profit__sum'] is None:
            totalProfitUSDSum['profit__sum'] = 0.0

        response['totalProfitUSD'] =round(totalProfitUSDSum['profit__sum'],1)

        response['closedTradeLong'] = transactionsDataTotalLong.count()
        response['closedTradeShort'] = transactionsDataTotalShort.count()

        response['initialCapitalUSDLong'] = instance.initialCapitalUSDLong
        response['initialCapitalUSDShort'] = instance.initialCapitalUSDShort

        transactionsDataTotalLongSum = transactionsDataTotalLong.aggregate(Sum('profit'))

        if transactionsDataTotalLongSum['profit__sum'] is None:
            transactionsDataTotalLongSum['profit__sum']  = 0.0

        response['quantityUSDLong'] = instance.initialCapitalUSDShort + round(transactionsDataTotalLongSum['profit__sum'],1)

        transactionsDataTotalShortSum = transactionsDataTotalShort.aggregate(Sum('profit'))
        if transactionsDataTotalShortSum['profit__sum'] is None:
            transactionsDataTotalShortSum['profit__sum'] = 0.0
            
        response['quantityUSDShort'] = instance.initialCapitalUSDShort + round(transactionsDataTotalShortSum['profit__sum'],1)



        transactionsDataTotalLongSumPorcentage = transactionsDataTotalLong.aggregate(Sum('profit_percentage'))
        if transactionsDataTotalLongSumPorcentage['profit_percentage__sum'] is None:
            transactionsDataTotalLongSumPorcentage['profit_percentage__sum']  = 0.0

        transactionsDataTotalShortSumPorcentage = transactionsDataTotalShort.aggregate(Sum('profit_percentage'))
        if transactionsDataTotalShortSumPorcentage['profit_percentage__sum'] is None:
            transactionsDataTotalShortSumPorcentage['profit_percentage__sum'] = 0.0


        response['profitPorcentageLong'] = round(transactionsDataTotalLongSumPorcentage['profit_percentage__sum'],1)
        response['profitPorcentageShort'] = round(transactionsDataTotalShortSumPorcentage['profit_percentage__sum'],1)
            

        response['id'] = instance.id

        return response


class strategySerializers(serializers.ModelSerializer):

    class Meta:
        model = strategy

        fields = [
            'strategy',
            'order',
            'contracts',
            'ticker',
            'position_size',
        ]


