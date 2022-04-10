
# Import Other packages
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from utils.convert_json_to_objects import convertJsonToObject

from apps.authentication.models import User
from apps.broker.broker_close_trade import broker_close_trade_alpaca
from apps.broker.broker_short_alpaca import broker_sell_short_alpaca
from apps.broker.broker_short_papertrade import (broker_short_buy_papertrade,
                                                 broker_short_sell_papertrade)
# Import Brokers
from apps.broker.brokers_connections.alpaca.long_buy import \
    broker as broker_alpaca
from apps.broker.brokers_connections.paper_trade.long_buy import broker as papertrade
from apps.broker.brokers_connections.paper_trade.short import broker as papertrade_short

from apps.broker.models import broker

# from apps.broker.utils.papertrade import papertrade

from apps.strategy.models import strategyNews, symbolStrategy
# Import Models Utils
from apps.trading.models import strategy, trading_config
from apps.trading.serializers import (strategySerializers,
                                      tradingConfigSerializerPut,
                                      tradingConfigSerializers)


# Create your views here.
class tradingConfigViews(generics.ListCreateAPIView):

    serializer_class = tradingConfigSerializers
    queryset = trading_config.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)

    # Create post method
    def post(self, request):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication request or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = request.user.id
        body = request.data
        body['owner'] = userId

        # RuleJs of quantity or national
        # Get strategyNew Id:
        try:
            strategy = strategyNews.objects.get(
                id=body['strategyNews'])
        except:
            # Return
            return Response({
                "status": "error",
                "message": "Strategy not found",
            }, status=status.HTTP_204_NO_CONTENT)

        trading_config_obj = trading_config.objects.filter(
            owner_id=userId, strategyNews_id=body['strategyNews'])

        # Validate not exist inside of db this owner_id with this strategyNews_id
        if trading_config_obj.count() > 0:
            return Response({
                "status": "not allowed",
                "message": "This trading_config already exist",
            }, status=status.HTTP_226_IM_USED
            )

        # Get restrictions from the broker.
        broker_obj = broker.objects.get(id=request.data['broker'])

        trade_rules = {
            "short_is_allowed": broker_obj.short_is_allowed,
            "short_allowed_fractional": broker_obj.short_allowed_fractional,
            "long_is_allowed": broker_obj.long_is_allowed,
            "long_allowed_fractional": broker_obj.long_allowed_fractional,
            "short_is_allowed_crypto": broker_obj.short_is_allowed_crypto,
            "short_allowed_fractional_crypto": broker_obj.short_allowed_fractional_crypto,
            "long_is_allowed_crypto": broker_obj.long_is_allowed_crypto,
            "long_allowed_fractional_crypto": broker_obj.long_allowed_fractional_crypto,
        }

        is_crypto = strategy.symbol.is_crypto

        # Rules for verify if is allowed the trade
        rules_controller = [
            {
                "is_crypto": True,
                "variable_false": 'short_is_allowed_crypto',
                "message": "The broker not allow the short crypto trade",
                "request_data_variable": "is_active_short"
            },
            {
                "is_crypto": True,
                "variable_false": "long_is_allowed_crypto",
                "message": "The broker not allow the long crypto trade",
                "request_data_variable": "is_active_long"
            },
            {
                "is_crypto": False,
                "variable_false": "long_is_allowed",
                "message": "The broker not allow the long trade",
                "request_data_variable": "is_active_long"
            },
            {
                "is_crypto": False,
                "variable_false": "short_is_allowed",
                "message": "The broker not allow the short trade",
                "request_data_variable": "is_active_short"
            },
        ]

        # Check if is allowed the trade if is not crypto trade
        for rule in rules_controller:
            if rule['is_crypto'] == is_crypto:
                if not getattr(broker_obj, rule['variable_false']):

                    if request.data[rule['request_data_variable']] == True:
                        return Response({
                            "status": "error",
                            "message": rule['message'],
                            "trade_rules": trade_rules
                        }, status=status.HTTP_400_BAD_REQUEST)

        rule_controller = [
            {
                "is_crypto": True,
                "variable_false": "short_allowed_fractional_crypto",
                "mandatory_variable": "quantityQTYShort",
                "is_interger_value": False,
                "message": "The broker not allow the fractional crypto trade"
            },
            {
                "is_crypto": True,
                "variable_false": "long_allowed_fractional_crypto",
                "mandatory_variable": "quantityQTYLong",
                "is_interger_value": False,
                "message": "The broker not allow the fractional crypto trade"
            },
            {
                "is_crypto": False,
                "variable_false": "short_allowed_fractional",
                "mandatory_variable": "quantityQTYShort",
                "is_interger_value": False,
                "message": "The broker not allow the fractional trade"
            },
            {
                "is_crypto": False,
                "variable_false": "long_allowed_fractional",
                "mandatory_variable": "quantityQTYLong",
                "is_interger_value": False,
                "message": "The broker not allow the fractional trade"
            },
        ]

        # TODO test this controller.
        for rule in rule_controller:
            if rule['is_crypto'] == is_crypto:
                if not getattr(broker_obj, rule['variable_false']):
                    if not rule['is_interger_value']:

                        value_qty = body.get(rule['mandatory_variable'])

                        if not body.get(rule['mandatory_variable']):
                            # Return one error, not is allowed the fractional trade
                            return Response({
                                "status": "error",
                                "message": rule['message'],
                                "trade_rules": trade_rules
                            }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if not body.get(rule['mandatory_variable']):
                            # Return one error, not is allowed the fractional trade
                            return Response({
                                "status": "error",
                                "message": rule['message'],
                                "trade_rules": trade_rules
                            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = tradingConfigSerializers(data=body)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Add this follower inside of the strategyNews in manyToManyField  Follower
            try:
                strategyNews(
                    id=body['strategyNews']).follower.add(userId)
            except Exception as e:
                print(e)
                print('The user is follower')

            return Response({
                "status": "success",
                "message": "Trading Parameter created successfully",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "status": "error",
                "message": "Trading Parameter not created",
                "data": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

    # Create method get all
    def get(self, request):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication request or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = request.user.id
        body = request.data
        body['owner'] = userId

        # Filter data only by owner_id
        data = trading_config.objects.filter(owner=userId).values()

        return Response({
            "status": "success",
            "message": "Trading Parameter list",
            "results": data,
        }, status=status.HTTP_200_OK)


class tradingConfigSlugViews(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = tradingConfigSerializers
    queryset = trading_config.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)

    # Create method delete by id
    def delete(self, request, slug):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication request or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = request.user.id
        body = request.data
        body['owner'] = userId

        # Filter data only by owner_id
        data = trading_config.objects.filter(owner_id=userId, id=slug)

        if data.count() == 0:
            return Response({
                "status": "error",
                "message": "Trading Parameter not found",
            }, status=status.HTTP_204_NO_CONTENT)

        data.delete()

        return Response({
            "status": "success",
            "message": "Trading Parameter deleted successfully",
        }, status=status.HTTP_200_OK)

    # Create method update by id
    def put(self, request, slug):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication request or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            trading_config_obj = trading_config.objects.get(
                owner_id=request.user.id, id=slug)
        except Exception as e:
            trading_config_obj = None

        if trading_config_obj == None:
            return Response({
                "status": "error",
                "message": "Trading Parameter not found",
            }, status=status.HTTP_204_NO_CONTENT)

        serializer = tradingConfigSerializerPut(
            trading_config_obj, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                "status": "success",
                "message": "Trading Parameter updated successfully",
                "data": serializer.data,
            }, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({
                "status": "error",
                "message": "Trading Parameter not updated",
                "data": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)


class tradingConfigGetAllViews(generics.ListAPIView):

    serializer_class = tradingConfigSerializers
    queryset = trading_config.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):

        if self.request.auth == None:

            return Response({
                "status": "error",
                "message": "Authentication request or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user

        return trading_config.objects.filter(owner_id=user.id)


class strategyView(generics.GenericAPIView):

    serializer_class = strategySerializers
    queryset = strategy.objects.all()
    permission_classes = (permissions.AllowAny, )

    def post(self, request):

        data = request.data

        strategyNewsConfig = strategyNews.objects.filter(
            strategy_token=data['token'])

        if strategyNewsConfig.count() == 0:
            return Response({
                "status": "error",
                "message": "Token Not found",
            }, status=status.HTTP_204_NO_CONTENT)

        # Get List of users for this strategy

        # Check if this strategy is active:
        if strategyNewsConfig.values()[0]['is_active'] == False:
            return Response({
                "status": "error",
                "message": "Strategy not active",
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Get list of Follower for this strategy from ManyToManyField django object
        strategyData = strategyNews.objects.get(
            strategy_token=data['token'])

        followers = strategyData.follower.all()

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

        are_followers = False
        for follow in followers:
            are_followers = True

            strategyNewsId = strategyNewsConfig.values()[0]['id']
            # Check if this user
            tradingConfig = trading_config.objects.get(
                owner_id=follow.id, strategyNews_id=strategyNewsId)

            if tradingConfig.is_active == True:

                quantityUSD = tradingConfig.quantityUSDLong
                use = tradingConfig.useLong
                stopLoss = tradingConfig.stopLossLong
                takeProfit = tradingConfig.takeProfitLong
                consecutiveLosses = tradingConfig.consecutiveLossesLong
                brokerName = tradingConfig.broker.broker
                brokerCapital = tradingConfig.broker.capital

                options = {
                    "owner_id": follow.id,
                    "strategyNews_id": strategyNewsConfig.values()[0]['id'],
                    "quantityUSD": quantityUSD,
                    "use": use,
                    "stopLoss": stopLoss,
                    "takeProfit": takeProfit,
                    "consecutiveLosses": consecutiveLosses,
                    "brokerCapital": brokerCapital,
                    "symbol": strategyData.symbol.symbolName_corrected
                }

                options = convertJsonToObject(options)

                # Create one Long Trade
                if data['order'] == 'buy' and tradingConfig.is_active_long == True:

                    options.order = 'buy'
                    # Open Long Positions
                    if brokerName == "paperTrade":
                        # Open Long Trade [PAPERTRADE-BUY]
                        results = papertrade(
                            trading=tradingConfig,
                            strategy=strategyData,
                            operation='long'
                        ).long_buy(
                            options=options,
                            results=results
                        )

                    if brokerName == 'alpaca':
                        # Open Long Trade [ALPACA-BUY]
                        results = broker_alpaca(
                            options=options,
                            strategy=strategyData,
                            trading=tradingConfig,
                            results=results,
                            operation='long'
                        ).long_buy()

                if data['order'] == 'sell' and tradingConfig.is_active_long == True:

                    # Sell Short
                    if brokerName == "paperTrade":
                        # Open Short Trade [PAPERTRADE-SELL]

                        results = papertrade(
                            trading=tradingConfig,
                            strategy=strategyData,
                            operation='long'
                        ).close_position(
                            options=options,
                            results=results,
                        )

                    if brokerName == 'alpaca':

                        # CLOSE LONG TRADE [ALPACA-SELL]
                        results = broker_alpaca(
                            options=options,
                            strategy=strategyData,
                            trading=tradingConfig,
                            results=results,
                            operation='long'
                        ).close_position()

                if data['order'] == 'sell' and tradingConfig.is_active_short == True:

                    options.order = 'sell'

                    if brokerName == "paperTrade":
                        results = papertrade_short(
                            trading=tradingConfig,
                            strategy=strategyData,
                            options=options,
                            results=results
                        ).short_buy()

                    if brokerName == 'alpaca':

                        broker_sell_short_alpaca({
                            "order": "sell",
                            "owner_id": follow.id,
                            "strategyNews_id": strategyNewsConfig.values()[0]['id'],
                            "quantityUSD": quantityUSD,
                            "use": use,
                            "stopLoss": stopLoss,
                            "takeProfit": takeProfit,
                            "consecutiveLosses": consecutiveLosses,
                            "brokerCapital": brokerCapital,
                            "symbol": strategyData.symbol.symbolName_corrected
                        },
                            strategyData,
                            tradingConfig,
                            results)

                if data['order'] == 'buy' and tradingConfig.is_active_short == True:
                    options.order = 'buy'

                    if brokerName == "paperTrade":

                        results = papertrade_short(
                            trading=tradingConfig,
                            strategy=strategyData,
                            options=options,
                            results=results
                        ).close_position()

                        # broker_short_buy_papertrade({
                        #     "order": "sell",
                        #     "owner_id": follow.id,
                        #     "strategyNews_id": strategyNewsConfig.values()[0]['id'],
                        #     "quantityUSD": quantityUSD,
                        #     "use": use,
                        #     "stopLoss": stopLoss,
                        #     "takeProfit": takeProfit,
                        #     "consecutiveLosses": consecutiveLosses,
                        #     "brokerCapital": brokerCapital,
                        #     "symbol": strategyData.symbol.symbolName_corrected
                        # },
                        #     strategyData,
                        #     tradingConfig,
                        #     results
                        # )

                    if brokerName == 'alpaca':
                        broker_close_trade_alpaca({
                            "order": "sell",
                            "owner_id": follow.id,
                            "strategyNews_id": strategyNewsConfig.values()[0]['id'],
                            "quantityUSD": quantityUSD,
                            "use": use,
                            "stopLoss": stopLoss,
                            "takeProfit": takeProfit,
                            "consecutiveLosses": consecutiveLosses,
                            "brokerCapital": brokerCapital,
                            "symbol": strategyData.symbol.symbolName_corrected
                        },
                            strategyData,
                            tradingConfig,
                            results,
                            operation='short'
                        )

        if are_followers:
            return Response({
                "status": "success",
                "message": "Strategy executed successfully",
                "data": results,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "warning",
                "message": "Strategy not have any follower",
                "data": results,
            }, status=status.HTTP_204_NO_CONTENT)
