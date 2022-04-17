import datetime
from itertools import count
import json
import random
import string
import time
from datetime import datetime, timezone

import alpaca_trade_api as tradeapi
import requests

from apps.authentication.api.serializers import (LoginSerializer,
                                                 RegisterSerializer,
                                                 UserSocialSerializer)

from apps.authentication.api.views import LoginAPIView, RegisterViewSet

from apps.authentication.models import User

from apps.broker.api.views import (alpacaConfigurationSerializersView,
                                   brokerSerializersView)
# Create test for createStrategy
from apps.broker.models import broker as broker_model
from apps.strategy.api.views import PostSettingAPIview

from apps.strategy.models import symbolStrategy, strategyNews as strategy_model
from apps.trading.models import trading_config as trading_config_model


from apps.trading.views import (strategy_view, trading_config_get_all_view,
                                trading_config_slug_views, trading_config_view)

from apps.transaction.models import transactions

from apps.transaction.updater import \
    scheduler_transactions_updated_calculate_profit

# import settings.

# Get Configuration from django settings
from backend import settings

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework.test import (APIClient, APIRequestFactory, APITestCase,
                                 force_authenticate)

from utils.brokers import broker_alpaca
from utils.by_tests.select_test_material import trading_random_image
from utils.convert_json_to_objects import convertJsonToObject
from utils.test_components.functionalities_utils import functionalities

import pytz
import datetime

from backend import settings


class TradingAlpacaLongCreateStrategy(APITestCase):

    def setUp(self):
        # Create random name and email
        self.name = "Hensley"
        self.password = "Passw0rd!"
        self.email = "ava_1946463933@test.com"

        #! Close all alpaca positions
        self.endpoint = "https://paper-api.alpaca.markets"
        self.api = tradeapi.REST(settings.ALPACA_BROKER_TEST_API_KEY_ID,
                                 settings.ALPACA_BROKER_TEST_SECRET_KEY, self.endpoint)

        self.api.close_all_positions()

        # Create new user.
        response_new_user = functionalities.create_user(
            self.name, self.password, self.email)

        self.response_new_user = response_new_user

        self.assertEqual(response_new_user.status_code,
                         status.HTTP_201_CREATED)

        response_login = functionalities.login_user(
            email=self.email, password=self.password)
        self.response_login = response_login

        self.token_access = response_login.data['token_access']

        self.assertEqual(response_login.status_code,
                         status.HTTP_200_OK)

        self.user = User.objects.get(
            username=self.name,
            email=self.email,
        )

        self.body = {
            'strategyNews': 'AlpacaLongETHUSD',
            'description': 'simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
            'user': self.user.id,
            'is_public': True,
            'is_active': True,
            'net_profit': 1.3,
            'percentage_profitable': 0.5,
            'max_drawdown': 3,
            'period': 'hour',
            'timer': '1',
        }

        brokerNumbers = broker_model.objects.filter(
            owner_id=self.user.id, broker='paperTrade').count()

        self.assertEqual(brokerNumbers, 1)

    def test_long_buy_crypto(self):

        if settings.test_long_buy_crypto:

            #!  Create Strartegy
            symbol = 'SOLUSD'

            self.body['symbol'] = symbol

            response_create_strategy = functionalities.create_strategy(
                symbol, body=self.body, user_id=self.user.id, token_access=self.token_access)

            response_strategyNews = response_create_strategy.data
            strategyNewsId = response_strategyNews['data']['strategyNewsId']
            self.assertEqual(response_create_strategy.status_code,
                             status.HTTP_200_OK)

            # ? Create Broker
            #! Create Alpaca Broker.  alpaca
            response_create_broker = functionalities.create_broker(
                self.token_access)

            #! Response Create Trading Config
            broker_id = response_create_broker.data['results']['id']

            tradingConfigBody = {
                "strategyNews": strategyNewsId,
                "broker": broker_id,
                "quantityUSDLong": 1000,
                "useLong": True,
                "stopLossLong": -5,
                "takeProfitLong": 10,
                "consecutiveLossesLong": 3,
                "quantityQTYShort": 2,  # * This parameter is not allowed.
                "useShort": False,
                "stopLossShort": -5,
                "takeProfitShort": 10,
                "consecutiveLossesShort": 3,
                "is_active": True,
                "is_active_short": False,
                "is_active_long": True,
                "close_trade_long_and_deactivate": True,
                "close_trade_short_and_deactivate": True
            }

            response_trading_config = functionalities.create_trading_config(
                strategy_id=strategyNewsId,
                broker_id=broker_id,
                token_access=self.token_access,
                tradingConfigBody=tradingConfigBody
            )

            self.assertEqual(response_trading_config.status_code, 201)

            #! Build the body for create trading operation
            body_open_transaction = response_create_strategy.create_trade_body

            #! Create Buy Alpaca-Broker Transaction trade_push_with_strategy
            response_create_trade = functionalities.create_trade(
                body_open_transaction, 'buy')

            self.assertEqual(
                response_create_trade.status_code, status.HTTP_200_OK)

            response_create_trade.data = convertJsonToObject(
                response_create_trade.data)

            self.assertEqual(response_create_trade.data.status, 'success')

            # ? Check if the transaction is opened
            self.assertEqual(
                response_create_trade.data.data.long.transaction_opened > 0, True)

            # Get symbol data
            symbol_data = functionalities.get_symbol(symbol)

            transaction = transactions.objects.filter(
                owner_id=self.user.id,
                strategyNews_id=strategyNewsId,
                broker_id=broker_id,
                symbol_id=symbol_data.id,
                isClosed__in=[False]
            ).order_by('-id')

            transaction_count = transaction.count()
            transaction_values = transaction.values()[0]

            # ? Validate if exist one transaction
            self.assertEqual(transaction_count > 0, True)
            self.assertEqual(transaction_values['order'], 'buy')
            self.assertEqual(transaction_values['operation'], 'long')

            #! Check if idTransaction is equal to alpaca id
            alpaca_orders = self.api.get_order(
                transaction_values['idTransaction'])
            self.assertEqual(alpaca_orders.id,
                             transaction_values['idTransaction'])

            #! Close the transation [SELL]
            response_trading_strategy = functionalities.create_trade(
                body_open_transaction, 'sell')

            # ? Verify the code 200
            self.assertEqual(
                response_trading_strategy.status_code, status.HTTP_200_OK)

    def test_calibrate_spread_not_crypto(self):

        if settings.test_calibrate_spread_not_crypto:
            # List of symbolrs not crypto, for example AAPL, FB, TSLA and others
            symbols = ['AAPL', 'FB', 'TSLA', 'AMZN']

            # buy_list = [
            #     # AAPL None 1000
            #     {
            #         'symbol': 'AAPL',
            #         'quantity': None,
            #         'usd': 1000
            #     },
            #     # FB 2 None
            #     {
            #         'symbol': 'FB',
            #         'quantity': 2,
            #         'usd': None
            #     },
            #     # AMZN None 1000
            #     {
            #         'symbol': 'AMZN',
            #         'quantity': None,
            #         'usd': 1000
            #     },
            #     # TSLA None 1000
            #     {
            #         'symbol': 'TSLA',
            #         'quantity': None,
            #         'usd': 1000
            #     },
            #     # SPY 2 None
            #     {
            #         'symbol': 'SPY',
            #         'quantity': 2,
            #         'usd': None
            #     },
            #     # GLD 5 None
            #     {
            #         'symbol': 'GLD',
        #         'quantity': 5,
        #         'usd': None
        #     },
        #     # NFLX None 2000
        #     {
        #         'symbol': 'NFLX',
        #         'quantity': None,
        #         'usd': 2000
        #     },
        #     # SPOT 4 None
        #     {
        #         'symbol': 'SPOT',
        #         'quantity': 4,
        #         'usd': None
        #     },

        # ]

            buy_list = [
                # AAPL None 1000
                # {
                #     'symbol': 'BTCUSD',
                #     'quantity': None,
                #     'usd': 4000
                # },
                {
                    'symbol': 'SOLUSD',
                    'quantity': 4,
                    'usd': None
                },
                # {
                #     'symbol': 'ETHUSD',
                #     'quantity': None,
                #     'usd': 1000
                # },
            ]

            tradingConfigBody = {
                "strategyNews": 0,
                "broker": 0,
                "useLong": True,
                "stopLossLong": -5,
                "takeProfitLong": 10,
                "consecutiveLossesLong": 3,
                "consecutiveLossesShort": 3,
                "is_active": True,
                "is_active_short": False,
                "is_active_long": True,
            }

            
            body = self.body
            # Run this test only when new york market is open with newyork time region America/New_York and import the dependencies

            time_now_zone = datetime.datetime.now(
                pytz.timezone("America/New_York"))
            hour = time_now_zone.hour

            strategy_list = []
            response_data_buy = []
            count = 0
            # if hour >= 9 and hour <= 16:
            if True:  # TODO active this after.

                for i in buy_list:
                    count += 1

                    d = convertJsonToObject(i)
                    # Symbol replace of body
                    body['symbol'] = d.symbol
                    body['strategyNews'] = d.symbol

                    #! Create strategy:
                    response_create_strategy = functionalities.create_strategy(
                        d.symbol, body=self.body, user_id=self.user.id, token_access=self.token_access)

                    self.assertEqual(
                        response_create_strategy.status_code, status.HTTP_200_OK)

                    data_response = convertJsonToObject(
                        response_create_strategy.data)

                    #! Create broker config
                    if count == 1:
                        response_create_broker = functionalities.create_broker(
                            self.token_access)
                        self.assertEqual(
                            response_create_broker.status_code, status.HTTP_201_CREATED)

                        broker_id = response_create_broker.data['results']['id']

                    #! Create trading config

                    tradingConfigBody['strategyNews'] = data_response.data.strategyNewsId
                    tradingConfigBody['broker'] = broker_id
                    tradingConfigBody['is_active_short'] = False

                    if d.quantity is not None:
                        tradingConfigBody['quantityQTYLong'] = d.quantity
                    elif d.usd is not None:
                        tradingConfigBody['quantityUSDLong'] = d.usd

                    
                    response_trading_config = functionalities.create_trading_config(
                        strategy_id=data_response.data.strategyNewsId,
                        broker_id=broker_id,
                        token_access=self.token_access,
                        tradingConfigBody=tradingConfigBody
                    )

                    self.assertEqual(
                        response_trading_config.status_code, status.HTTP_201_CREATED)

                    # #! Buy the strategy
                    response_buy = functionalities.create_trade(
                        trade_type='buy', token=data_response.data.strategy_token)

                    self.assertEqual(
                        response_buy.status_code, status.HTTP_200_OK)

                    # Get the bot email

                    strategy_obj = strategy_model.objects.get(
                        id=data_response.data.strategyNewsId)
                    user_obj = User.objects.get(email=self.user.email)

                    # * Disabled trading short
                    functionalities.disabled_buy_or_short_trading_config(
                        user_id=user_obj.id,
                        strategyNews_id=strategy_obj.id,
                        disabled_short=True,
                    )

                    # Update the trading_config_obj_bot inside of the django database
                    trading_config_obj_bot = trading_config_model.objects.get(
                        owner_id=user_obj.id, strategyNews_id=strategy_obj.id)
                    # initialCapitalQTYLong
                    trading_config_obj_bot.initialCapitalQTYLong = d.quantity
                    # initialCapitalUSDLong
                    trading_config_obj_bot.initialCapitalUSDLong = d.usd
                    # Save new data.
                    trading_config_obj_bot.save()

                    strategy_list.append({
                        'symbol': d.symbol,
                        'quantity': d.quantity,
                        'usd': d.usd,
                        'strategy_token': data_response.data.strategy_token,
                        'strategyNewsId': data_response.data.strategyNewsId,
                        'status_code': response_buy.status_code,
                        'bot_email': strategy_obj.email_bot,
                        'bot_user_id': user_obj.id,
                        'trading_confing_id': trading_config_obj_bot.id,

                    })

                # Disabled all shorts.
                # Sell all Strategies.

                for i in strategy_list:
                    d = convertJsonToObject(i)
                    response_sell = functionalities.create_trade(
                        trade_type='sell', token=d.strategy_token)

                    scheduler_transactions_updated_calculate_profit()

                    self.assertEqual(
                        response_sell.status_code, status.HTTP_200_OK)

                    response_transactions = transactions.objects.filter(
                        strategyNews_id=d.strategyNewsId).values()

                    for transaction_i in response_transactions:

                        data_i = convertJsonToObject(i)
                        transaction_d = transactions.objects.get(
                            id=transaction_i['id']
                        )

                        # Run Job for calculate profit
                        data_i.broker = transaction_d.broker.broker
                        # price_closed
                        data_i.price_closed = transaction_d.price_closed
                        # base_cost
                        data_i.base_cost = transaction_d.base_cost
                        # price_closed
                        data_i.price_closed = transaction_d.price_closed
                        # qty_close
                        data_i.qty_close = transaction_d.qty_close
                        # profit
                        data_i.profit = transaction_d.profit
                        # profit_percentage
                        data_i.profit_percentage = transaction_d.profit_percentage

                        response_data_buy.append(data_i)
                        print("@Note-01 ---- 67629203 -----")

            # Calculate the delta btw alpaca and tradingview positions.
            broker_alpaca = []
            broker_papertrade = []
            for response in response_data_buy:
                if response.broker == 'alpaca':
                    # append the broker alpaca
                    broker_alpaca.append(response)
                elif response.broker == 'paperTrade':
                    broker_papertrade.append(response)

            # Calculate the difference
            delta_brokers = []
            for i in range(0, len(broker_alpaca), 1):

                alpaca = broker_alpaca[i]
                papertrade = broker_papertrade[i]

                delta_profit = alpaca.profit - papertrade.profit
                delta_profit_percentage = alpaca.profit_percentage - papertrade.profit_percentage
                delta_qty_close = alpaca.qty_close - papertrade.qty_close
                delta_base_cost = alpaca.base_cost - papertrade.base_cost
                delta_price_closed = alpaca.price_closed - papertrade.price_closed

                delta_brokers.append({
                    'delta_profit': delta_profit,
                    'delta_profit_percentage': delta_profit_percentage,
                    'delta_qty_close': delta_qty_close,
                    'delta_base_cost': delta_base_cost,
                    'delta_price_closed': delta_price_closed,
                    'symbol': alpaca.symbol})

            print(delta_brokers)

        # Search inside of the i object the symbol = 'BTCUSD'
