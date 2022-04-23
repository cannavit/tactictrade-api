import json
import random
import string
import time

import alpaca_trade_api as tradeapi
from django.test import RequestFactory
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
from apps.strategy.models import strategyNews as strategy_model
from apps.trading.models import trading_config
from apps.trading.views import (strategy_view, trading_config_get_all_view,
                                trading_config_slug_views, trading_config_view, tradingOpenLongView, tradingOpenShortView)
from apps.transaction.models import transactions
from apps.transaction.updater import \
    scheduler_transactions_updated_calculate_profit
# import django settings
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

# import settings in django
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

    def test_trading_open_long(self):

        if settings.test_trading_open_long:

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

            # Open Long Order

            #? Save the follow part in functionalities. 

            factory = RequestFactory()  

            url = reverse('trading_open_long', kwargs={'pk': response_trading_config.data['data']['id']  })

            request = factory.post(url,format='json',
                                    HTTP_AUTHORIZATION='Bearer {}'.format(self.token_access))

            responsetradingOpenLongView = tradingOpenLongView.as_view()

            response = responsetradingOpenLongView(request, pk=response_trading_config.data['data']['id'] )


            self.assertEqual(response.status_code, 200)

    def test_trading_open_short(self):

        if settings.test_trading_open_short:

            #!  Create Strartegy
            symbol = 'MSFT'

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
                "quantityQTYShort": 1,
                "useShort": True,
                "stopLossShort": -5,
                "takeProfitShort": 10,
                "consecutiveLossesShort": 3,
                "is_active": True,
                "is_active_short": True,
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

            # Open Long Order

            #? Save the follow part in functionalities. 

            factory = RequestFactory()

            url = reverse('trading_open_short', kwargs={'pk': response_trading_config.data['data']['id']  })

            request = factory.post(url,format='json',
                                    HTTP_AUTHORIZATION='Bearer {}'.format(self.token_access))

            responsetradingOpenLongView = tradingOpenShortView.as_view()

            response = responsetradingOpenLongView(request, pk=response_trading_config.data['data']['id'] )

            self.assertEqual(response.status_code, 200)

