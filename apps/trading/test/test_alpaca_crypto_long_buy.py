import json
import random
import string
import time

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
from apps.strategy.models import symbolStrategy
from apps.trading.views import (strategyView, tradingConfigGetAllViews,
                                tradingConfigSlugViews, tradingConfigViews)
from apps.transaction.models import transactions
# import settings.
# Get Configuration from django settings
from django.conf import settings
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
        alpaca_orders = self.api.get_order(transaction_values['idTransaction'])
        self.assertEqual(alpaca_orders.id, transaction_values['idTransaction'])

        #! Close the transation [SELL]
        response_trading_strategy = functionalities.create_trade(
            body_open_transaction, 'sell')

        # ? Verify the code 200
        self.assertEqual(
            response_trading_strategy.status_code, status.HTTP_200_OK)

            

    #     response_trading_strategy_data = response_trading_strategy.data['data']
    #     long_closed = response_trading_strategy_data['long']['transaction_closed']
    #     # ? Check if was close the transaction
    #     self.assertTrue(long_closed > 0)

    #     #! Get List of orders with alpaca api
    #     transaction_closed = transactions.objects.filter(
    #         owner_id=self.user.id,
    #         strategyNews_id=strategyNewsId,
    #         broker_id=broker_id,
    #         symbol_id=symbol_data.id,
    #     ).order_by('-id')

    #     transaction_closed_values = transaction_closed.values()[0]
    #     transaction_closed_values_profit = transaction_closed_values['profit']

    #     alpaca_list_order = self.api.list_orders(
    #         status='closed',
    #         limit=2,
    #         nested=True
    #     )

    #     amount_closed_open = float(
    #         alpaca_list_order[1]._raw['filled_avg_price']) * float(alpaca_list_order[1]._raw['filled_qty'])
    #     amount_closed_closd = float(
    #         alpaca_list_order[0]._raw['filled_avg_price']) * float(alpaca_list_order[0]._raw['filled_qty'])
    #     profit_alpaca_long = amount_closed_closd - amount_closed_open

    # def test_trading_config_edit(self):

    #     # * Preporesing test
    #     #!  Create Strartegy
    #     symbol = 'ETHUSD'
    #     self.body['symbol'] = symbol

    #     response_create_strategy = functionalities.create_strategy(
    #         symbol, body=self.body, user_id=self.user.id, token_access=self.token_access)

    #     response_strategyNews = response_create_strategy.data
    #     strategyNewsId = response_strategyNews['data']['strategyNewsId']
    #     self.assertEqual(response_create_strategy.status_code,
    #                      status.HTTP_200_OK)

    #     # ? Create Broker
    #     #! Create Alpaca Broker.  alpaca
    #     response_create_broker = functionalities.create_broker(
    #         self.token_access)

    #     #! Response Create Trading Config
    #     broker_id = response_create_broker.data['results']['id']

    #     response_trading_config = functionalities.create_trading_config(
    #         strategy_id=strategyNewsId,
    #         broker_id=broker_id,
    #         token_access=self.token_access)

    #     self.assertEqual(
    #         response_trading_config.status_code, status.HTTP_201_CREATED)

    #     # * Test edit trading config using one custom body.
    #     trading_config_id = response_trading_config.data['data']['id']

    #     #! Save only one parameters
    #     body = {
    #         "is_active_short": True,
    #         # "is_active_long": False
    #     }

    #     factory = APIRequestFactory()
    #     url = reverse('tradingValue_edit', kwargs={'slug': trading_config_id})

    #     request = factory.put(url, body, format='json',
    #                           HTTP_AUTHORIZATION='Bearer {}'.format(self.token_access))

    #     response = tradingConfigSlugViews.as_view()(request, slug=trading_config_id)

    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    #     #! Save all data

    #     body_full_data = {
    #         "quantityUSDLong": 600,
    #         "useLong": True,
    #         "stopLossLong": -5,
    #         "takeProfitLong": 10,
    #         "consecutiveLossesLong": 3,
    #         "quantityUSDShort": 500,
    #         "useShort": True,
    #         "stopLossShort": -5,
    #         "takeProfitShort": 0,
    #         "consecutiveLossesShort": 3,
    #         "is_active": True,
    #         "is_active_short": True,
    #         "is_active_long": True,
    #         "close_trade_long_and_deactivate": True,
    #         "close_trade_short_and_deactivate": True
    #     }

    #     factory = APIRequestFactory()
    #     url = reverse('tradingValue_edit', kwargs={'slug': trading_config_id})

    #     request = factory.put(url, body_full_data, format='json',
    #                           HTTP_AUTHORIZATION='Bearer {}'.format(self.token_access))

    #     response = tradingConfigSlugViews.as_view()(request, slug=trading_config_id)

    #     self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    #     #! Control of bad request

    #     factory = APIRequestFactory()
    #     url = reverse('tradingValue_edit', kwargs={'slug': 100})

    #     request = factory.put(url, body_full_data, format='json',
    #                           HTTP_AUTHORIZATION='Bearer {}'.format(self.token_access))

    #     response = tradingConfigSlugViews.as_view()(request, slug=100)

    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
