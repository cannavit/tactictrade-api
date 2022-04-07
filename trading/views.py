
# Import Serializers Utils
import json
from authentication.models import User
from trading.serializers import tradingConfigSerializerPut, tradingConfigSerializers, strategySerializers
# Import Models Utils
from trading.models import trading_config, strategy
from strategy.models import strategyNews
# Import Other packages
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from broker.utils.papertrade import papertrade
from broker.broker_short_papertrade import broker_short_sell_papertrade, broker_short_buy_papertrade
from broker.broker_long_alpaca import broker_buy_alpaca
from broker.broker_short_alpaca import broker_sell_short_alpaca
from broker.broker_close_trade import broker_close_trade_alpaca


# Create your views here.
class tradingConfigViews(generics.ListCreateAPIView):

    serializer_class = tradingConfigSerializers
    queryset = trading_config.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)

    # Create post method
    def post(self, required):

        if required.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = required.user.id
        body = required.data
        body['owner'] = userId

        # Get strategyNew Id:
        strategyNewCount = strategyNews.objects.filter(
            id=body['strategyNews']).count()

        if strategyNewCount == 0:
            # Return
            return Response({
                "status": "error",
                "message": "Strategy not found",
            }, status=status.HTTP_204_NO_CONTENT)

        # Validate not exist inside of db this owner_id with this strategyNews_id
        if trading_config.objects.filter(
                owner_id=userId, strategyNews_id=body['strategyNews']).count() > 0:
            return Response({
                "status": "not allowed",
                "message": "This trading_config already exist",
            }, status=status.HTTP_226_IM_USED
            )

        # Valid data structure for trading_param

        body['initialCapitalUSDLong'] = body['quantityUSDLong']
        body['initialCapitalUSDShort'] = body['quantityUSDShort']
        body['winTradeLong'] = 0
        body['winTradeShort'] = 0
        body['closedTradeShort'] = 0
        body['closedTradeLong'] = 0
        body['profitPorcentageShort'] = 0
        body['profitPorcentageLong'] = 0

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
    def get(self, required):

        if required.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = required.user.id
        body = required.data
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
    def delete(self, required, slug):

        if required.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = required.user.id
        body = required.data
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
                "message": "Authentication required or invalid token",
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
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user

        return trading_config.objects.filter(owner_id=user.id)


class strategyView(generics.GenericAPIView):

    serializer_class = strategySerializers
    queryset = strategy.objects.all()
    permission_classes = (permissions.AllowAny, )

    def post(self, request):

        # Create random token

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
                # Create one Long Trade
                if data['order'] == 'buy' and tradingConfig.is_active_long == True:
                    # Buy Long
                    quantityUSD = tradingConfig.quantityUSDLong
                    use = tradingConfig.useLong
                    stopLoss = tradingConfig.stopLossLong
                    takeProfit = tradingConfig.takeProfitLong
                    consecutiveLosses = tradingConfig.consecutiveLossesLong
                    brokerName = tradingConfig.broker.broker
                    brokerCapital = tradingConfig.broker.capital

                    if brokerName == "paperTrade":
                        
                        results = papertrade(
                            trading=tradingConfig,
                            strategy=strategyData,
                            operation='long'
                        ).long_buy(
                            options={
                            "order": "buy",
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
                            results=results
                        )

                    if brokerName == 'alpaca':

                        broker_buy_alpaca({
                            "order": "buy",
                            "owner_id": follow.id,
                            "strategyNews_id": strategyNewsConfig.values()[0]['id'],
                            "quantityUSD": quantityUSD,
                            "use": use,
                            "stopLoss": stopLoss,
                            "takeProfit": takeProfit,
                            "consecutiveLosses": consecutiveLosses,
                            "brokerCapital": brokerCapital,
                            "symbol": strategyData.symbol.symbolName_corrected  # TODO change the symbol name
                        },
                            strategyData,
                            tradingConfig,
                            results)

                if data['order'] == 'sell' and tradingConfig.is_active_long == True:

                    # Sell Short
                    quantityUSD = tradingConfig.quantityUSDLong
                    use = tradingConfig.useLong
                    stopLoss = tradingConfig.stopLossLong
                    takeProfit = tradingConfig.takeProfitLong
                    consecutiveLosses = tradingConfig.consecutiveLossesLong
                    brokerName = tradingConfig.broker.broker
                    brokerCapital = tradingConfig.broker.capital
                    isPaperTrading = tradingConfig.is_paper_trading

                    if brokerName == "paperTrade":
                        
                        results = papertrade(
                            trading=tradingConfig,
                            strategy=strategyData,
                            operation='long'
                        ).long_sell(
                            options={
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
                            results=results,
                        )

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
                            operation='long'
                        )

                if data['order'] == 'sell' and tradingConfig.is_active_short == True:

                    quantityUSD = tradingConfig.quantityUSDShort
                    use = tradingConfig.useShort
                    stopLoss = tradingConfig.stopLossShort
                    takeProfit = tradingConfig.takeProfitShort
                    consecutiveLosses = tradingConfig.consecutiveLossesShort
                    brokerName = tradingConfig.broker.broker
                    brokerCapital = tradingConfig.broker.capital
                    isPaperTrading = tradingConfig.is_paper_trading

                    if brokerName == "paperTrade":

                        broker_short_sell_papertrade({
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
                            results
                        )

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

                    quantityUSD = tradingConfig.quantityUSDShort
                    use = tradingConfig.useShort
                    stopLoss = tradingConfig.stopLossShort
                    takeProfit = tradingConfig.takeProfitShort
                    consecutiveLosses = tradingConfig.consecutiveLossesShort
                    brokerName = tradingConfig.broker.broker
                    brokerCapital = tradingConfig.broker.capital
                    isPaperTrading = tradingConfig.is_paper_trading

                    if brokerName == "paperTrade":

                        broker_short_buy_papertrade({
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
                            results
                        )

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
