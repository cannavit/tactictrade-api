
# Import Other packages
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.broker.brokers_connections.trading_control import broker_selector
from apps.broker.models import broker
from apps.strategy.models import strategyNews
# Import Models Utils
from apps.trading.models import strategy, trading_config

from apps.trading.serializers import (strategySerializers,
                                      tradingConfigSerializerPut,
                                      tradingConfigSerializers)
from apps.trading.utils.trading_accions import trading_action


from apps.transaction.models import transactions as transaction_model
from utils.convert_json_to_objects import convertJsonToObject
# Create your views here.t

import json

# Import configuration for create dynamic view in fluttter app.

# Import json file of alpaca config
alpaca_long = json.load(open('apps/trading/trading_config_views/alpaca_long.json'))
alpaca_short = json.load(open('apps/trading/trading_config_views/alpaca_short.json'))
alpaca_short_crypto = json.load(open('apps/trading/trading_config_views/alpaca_short_crypto.json'))
alpaca_long_crypto = json.load(open('apps/trading/trading_config_views/alpaca_long_crypto.json'))

# Import json file for papertrade config
paperTrade_long = json.load(open('apps/trading/trading_config_views/paperTrade_long.json'))
paperTrade_short = json.load(open('apps/trading/trading_config_views/paperTrade_short.json'))
paperTrade_short_crypto = json.load(open('apps/trading/trading_config_views/paperTrade_short_crypto.json'))
paperTrade_long_crypto = json.load(open('apps/trading/trading_config_views/paperTrade_long_crypto.json'))

class trading_config_flutter_view(generics.ListCreateAPIView):

    serializer_class = tradingConfigSerializers
    queryset = trading_config.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication request or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)     

        # Get the bro

        try:
            strategy_obj = strategyNews.objects.get(id=pk)
        except Exception as e:
            print(e)
            return Response({
                "status": "error",
                "message": "Strategy not found",
            }, status=status.HTTP_400_BAD_REQUEST)


        is_crypto = strategy_obj.symbol.is_crypto 

        # Import Json file for not crypto 
        if not is_crypto:
            # Read Json file
            paperTrade = {
                "long": paperTrade_long,
                "short": paperTrade_short,
            }

            alpaca = {
                "long": alpaca_long,
                "short": alpaca_short,
            }

        else:

            paperTrade = {
                "long": paperTrade_long_crypto,
                "short": paperTrade_short_crypto,
            }

            alpaca = {
                "long": alpaca_long_crypto,
                "short": alpaca_short_crypto,
            }

        return Response({
            "status": "success",
            "message": "Trading configs for view",
            "paperTrade": paperTrade,
            "alpaca": alpaca
        }, status=status.HTTP_200_OK)


class trading_config_view(generics.ListCreateAPIView):

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
        body["owner"] = userId

        # RuleJs of quantity or national
        # Get strategyNew Id:
        try:
            strategy = strategyNews.objects.get(
                id=body["strategyNews"])
        except Exception as e:
            # Return
            return Response({
                "status": "error",
                "message": "Strategy not found",
            }, status=status.HTTP_204_NO_CONTENT)

        trading_config_obj = trading_config.objects.filter(
            owner_id=userId, strategyNews_id=body["strategyNews"])

        # Validate not exist inside of db this owner_id with this strategyNews_id
        if trading_config_obj.count() > 0:
            return Response({
                "status": "not allowed",
                "message": "This trading_config already exist",
            }, status=status.HTTP_226_IM_USED
            )

        # Get restrictions from the broker.
        broker_obj = broker.objects.get(id=request.data["broker"])

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

        # rules_controller = [
        #     {
        #         "is_crypto": True,
        #         "variable_false": "short_is_allowed_crypto",
        #         "message": "The broker not allow the short crypto trade",
        #         "request_data_variable": "is_active_short"
        #     },
        #     {
        #         "is_crypto": True,
        #         "variable_false": "long_is_allowed_crypto",
        #         "message": "The broker not allow the long crypto trade",
        #         "request_data_variable": "is_active_long"
        #     },
        #     {
        #         "is_crypto": False,
        #         "variable_false": "long_is_allowed",
        #         "message": "The broker not allow the long trade",
        #         "request_data_variable": "is_active_long"
        #     },
        #     {
        #         "is_crypto": False,
        #         "variable_false": "short_is_allowed",
        #         "message": "The broker not allow the short trade",
        #         "request_data_variable": "is_active_short"
        #     },
        # ]

        # Check if is allowed the trade if is not crypto trade
        # for rule in rules_controller:
            # if rule["is_crypto"] == is_crypto:
                # if not getattr(broker_obj, rule["variable_false"]):

                    # if request.data[rule["request_data_variable"]] == True:
                        #TODO fix this controller
                        # print("@Note-01 ---- 320551155 -----")
                        # return Response({
                        #     "status": "error",
                        #     "message": rule["message"],
                        #     "trade_rules": trade_rules
                        # }, status=status.HTTP_400_BAD_REQUEST)

        # rule_controller = [
        #     {
        #         "is_crypto": True,
        #         "variable_false": "short_allowed_fractional_crypto",
        #         "mandatory_variable": "quantityQTYShort",
        #         "mandatory_usd_variable": "quantityUSDShort",
        #         "is_interger_value": False,
        #         "message": "The broker not allow the fractional crypto trade"
        #     },
        #     {
        #         "is_crypto": True,
        #         "variable_false": "long_allowed_fractional_crypto",
        #         "mandatory_variable": "quantityQTYLong",
        #         "mandatory_usd_variable": "quantityUSDLong",
        #         "is_interger_value": False,
        #         "message": "The broker not allow the fractional crypto trade"
        #     },
        #     {
        #         "is_crypto": False,
        #         "variable_false": "short_allowed_fractional",
        #         "mandatory_variable": "quantityQTYShort",
        #         "mandatory_usd_variable": "quantityUSDShort",
        #         "is_interger_value": False,
        #         "message": "The broker not allow the fractional trade"
        #     },
        #     {
        #         "is_crypto": False,
        #         "variable_false": "long_allowed_fractional",
        #         "mandatory_variable": "quantityQTYLong",
        #         "mandatory_usd_variable": "quantityUSDLong",
        #         "is_interger_value": False,
        #         "message": "The broker not allow the fractional trade"
        #     },
        # ]

        # TODO test this controller.
        # for rule in rule_controller:
        #     if rule["is_crypto"] == is_crypto:
        #         if not getattr(broker_obj, rule["variable_false"]):
        #             if not rule["is_interger_value"]:

        #                 value_qty = body.get(rule["mandatory_variable"])
        #                 #TODO create the test controller
        #                 # if not body.get(rule["mandatory_variable"]) and not body.get(rule["mandatory_usd_variable"]):
        #                 #     # Return one error, not is allowed the fractional trade
        #                 #     return Response({
        #                 #         "status": "error",
        #                 #         "message": rule["message"],
        #                 #         "trade_rules": trade_rules
        #                 #     }, status=status.HTTP_400_BAD_REQUEST)
        #             else:
        #                 if not body.get(rule["mandatory_variable"]):
        #                     # Return one error, not is allowed the fractional trade
        #                     return Response({
        #                         "status": "error",
        #                         "message": rule["message"],
        #                         "trade_rules": trade_rules
        #                     }, status=status.HTTP_400_BAD_REQUEST)

        serializer = tradingConfigSerializers(data=body)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # Add this follower inside of the strategyNews in manyToManyField  Follower
            try:
                strategyNews(
                    id=body["strategyNews"]).follower.add(userId)
            except Exception as e:

                print(e)
                print("The user is follower")

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
        body["owner"] = userId

        # Filter data only by owner_id
        data = trading_config.objects.filter(owner=userId).values()

        return Response({
            "status": "success",
            "message": "Trading Parameter list",
            "results": data,
        }, status=status.HTTP_200_OK)


class trading_config_slug_views(generics.RetrieveUpdateDestroyAPIView):

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
        body["owner"] = userId

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


class trading_config_get_all_view(generics.ListAPIView):

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

        # Get the parameter of the request
        category = self.request.query_params.get("category", None)

        try:
            if category == "active":
                results = trading_config.objects.filter(owner_id=user.id, is_active_short__in=[True], is_active_long__in=[True])
            elif category == "inactive":
                results = trading_config.objects.filter(owner_id=user.id, is_active_short__in=[False], is_active_long__in=[False])
            elif category == "winners":
                results = trading_config.objects.filter(owner_id=user.id, profitPorcentageShort__gte=0, profitPorcentageLong__gte=0)
            elif category == "losses":

                results = trading_config.objects.filter(owner_id=user.id, profitPorcentageShort__lte=0, profitPorcentageLong__lte=0)

            else:
                try:
                    results = trading_config.objects.filter(owner_id=user.id)
                except Exception as e:
                    print(e)
                    results = None


        except Exception as e:
            results = None
            return Response({
                "status": "error",
                "message": "Trading Parameter not found",
                "error": e
            }, status=status.HTTP_204_NO_CONTENT)
        


        print(results)
        return results


class strategy_view(generics.GenericAPIView):

    serializer_class = strategySerializers
    queryset = strategy.objects.all()
    permission_classes = (permissions.AllowAny, )

    def post(self, request):

        data = convertJsonToObject(request.data)

        try:
            strategy_obj = strategyNews.objects.get(
                strategy_token=data.token)
            strategy_exist = True
        except Exception as e:
            strategy_exist = False


        if not strategy_exist:
            return Response({
                "status": "error",
                "message": "Token Not found",
            }, status=status.HTTP_204_NO_CONTENT)

        # Get List of users for this strategy

        # Check if this strategy is active:
        if strategy_obj.is_active == False:
            return Response({
                "status": "error",
                "message": "Strategy not active",
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Get list of Follower for this strategy from ManyToManyField django object
        followers = strategy_obj.follower.all()

        response_data = {
                "messages": [],
                "errors": [],
                "closed_trades": 0,
                "errors_trade": 0,
            }

        are_followers = False
        code_response = 200

        for follow in followers:

            try:
                tradingConfig = trading_config.objects.get(
                    owner_id=follow.id, 
                    strategyNews_id=strategy_obj.id
                    )

                if tradingConfig.is_active == True:
                    try:
                        message_success = trading_action(tradingConfig, order=data.order)
                        response_data["messages"].append(message_success)
                        response_data["closed_trades"] += 1
                    except Exception as e:
                        code_response = 501
                        response_data["errors_trade"] += 1
                        response_data["errors"].append(str(e))
                # Transaction open
            except Exception as e:
                tradingConfig = None
     
        if code_response == 200:

            return Response({
                "status": "success",
                "message": response_data["messages"],
                "errors": response_data["errors"],
                "closed_trades": response_data["closed_trades"],
                "errors_trade": response_data["errors_trade"],
            }, status=status.HTTP_200_OK)

        else:

            return Response({
                "status": "warning",
                "message":response_data["messages"],
                "errors": response_data["errors"],
                "closed_trades": response_data["closed_trades"],
                "errors_trade": response_data["errors_trade"],
            }, status=status.HTTP_501_NOT_IMPLEMENTED)



class tradingOpenLongView(generics.GenericAPIView):

    serializer_class = strategySerializers
    queryset = strategy.objects.all()
    permission_classes = (permissions.AllowAny, )

    def post(self, request, pk):

        # Check if the token is valid 
        if self.request.auth== None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get parameter pk from request data django
        # TODO, Update the test for send the pk how parameter.
        trading_config_id = self.kwargs["pk"]
        print(trading_config_id)
        
        userId = request.user.id
        try: 
            trading_config_obj = trading_config.objects.get(id=trading_config_id, owner_id=userId)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Trading config not found"
            }, status=status.HTTP_404_NOT_FOUND)


        strategy_obj = trading_config_obj.strategyNews

        # Get Strategy News
        if strategy_obj.is_active == False:
            return Response({
                "status": "error",
                "message": "Strategy not active",
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

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
                "trade_type": "long",
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
                "trade_type": "short",
                "number_stocks": 0,
                "is_winner": False
            }
        }

        try:
            transaction_obj = transaction_model.objects.get(
                owner_id=userId,
                strategyNews_id=strategy_obj.id, 
                broker_id=trading_config_obj.broker.id,
                trading_config=trading_config_obj.id,
                symbol_id=strategy_obj.symbol.id,
                isClosed__in=[False],   
            )
            transaction_is_open = True
        except Exception as e:
            transaction_obj = None
            transaction_is_open = False

        broker_controller = broker_selector(
            trading_config=trading_config_obj,
            strategyNewsId=strategy_obj.id,
            follower_id=userId,
            strategyData=strategy_obj,
            transaction_is_open=transaction_is_open,
            transaction_obj=transaction_obj,
        )

        # Create one Long Trade
        results = broker_controller.long_trade(
            order="buy",
            broker_name=trading_config_obj.broker.broker,
            is_active_long=trading_config_obj.is_active_long,
            results=results,
        )

        # # Create Short Trade
        # results = broker_controller.short_trade(
        #     order=,
        #     broker_name=brokerName,
        #     is_active_short=tradingConfig.is_active_short,
        #     results=results,
        # )

        return Response({
            "status": "success",
            "message": "Strategy executed successfully",
            "data": results,
        }, status=status.HTTP_200_OK)


class tradingOpenShortView(generics.GenericAPIView):

    serializer_class = strategySerializers
    queryset = strategy.objects.all()
    permission_classes = (permissions.AllowAny, )

    def post(self, request, pk):

        # Check if the token is valid 
        if self.request.auth== None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get parameter pk from request data django
        # TODO, Update the test for send the pk how parameter.
        trading_config_id = self.kwargs["pk"]
        print(trading_config_id)
        
        userId = request.user.id
        try: 
            trading_config_obj = trading_config.objects.get(id=trading_config_id, owner_id=userId)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Trading config not found"
            }, status=status.HTTP_404_NOT_FOUND)


        strategy_obj = trading_config_obj.strategyNews

        # Get Strategy News
        if strategy_obj.is_active == False:
            return Response({
                "status": "error",
                "message": "Strategy not active",
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

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
                "trade_type": "long",
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
                "trade_type": "short",
                "number_stocks": 0,
                "is_winner": False
            }
        }

        try:
            transaction_obj = transaction_model.objects.get(
                owner_id=userId,
                strategyNews_id=strategy_obj.id, 
                broker_id=trading_config_obj.broker.id,
                trading_config=trading_config_obj.id,
                symbol_id=strategy_obj.symbol.id,
                isClosed__in=[False],   
            )
            transaction_is_open = True
        except Exception as e:
            transaction_obj = None
            transaction_is_open = False

        broker_controller = broker_selector(
            trading_config=trading_config_obj,
            strategyNewsId=strategy_obj.id,
            follower_id=userId,
            strategyData=strategy_obj,
            transaction_is_open=transaction_is_open,
            transaction_obj=transaction_obj,
        )

        # Create one Long Trade
        # results = broker_controller.long_trade(
        #     order="buy",
        #     broker_name=trading_config_obj.broker.broker,
        #     is_active_long=trading_config_obj.is_active_long,
        #     results=results,
        # )

        # # Create Short Trade
        results = broker_controller.short_trade(
            order="sell",
            broker_name=trading_config_obj.broker.broker,
            is_active_short=trading_config_obj.is_active_short,
            results=results,
        )

        return Response({
            "status": "success",
            "message": "Strategy executed successfully",
            "data": results,
        }, status=status.HTTP_200_OK)
