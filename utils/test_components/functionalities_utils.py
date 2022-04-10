import json
from apps.authentication.api.views import LoginAPIView, RegisterViewSet
from apps.authentication.models import User
from apps.broker.api.views import (alpacaConfigurationSerializersView)
# Create test for createStrategy
from apps.broker.models import broker as broker_model
from apps.strategy.api.views import PostSettingAPIview
from apps.strategy.models import symbolStrategy
from apps.trading.views import (strategyView,
                                 tradingConfigViews)
# import settings.
# Get Configuration from django settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import (APIClient, APIRequestFactory, APITestCase,
                                 force_authenticate)
from utils.brokers import broker_alpaca
from utils.by_tests.select_test_material import trading_random_image


class functionalities:

    def create_user(name, password, email):

        new_user_body = {
            "username": name,
            "password": password,
            "email": email,
            "first_name": "Buchanan",
            "last_name": "Bankss",
            "TEST_KEY": settings.TEST_KEY
        }

        factory = APIRequestFactory()
        request_new_user = factory.post(
            reverse('register_new_user'), new_user_body, format='json')
        response_new_user = RegisterViewSet.as_view()(request_new_user)

        return response_new_user

    def login_user(email, password):

        body = {
            "email": email,
            "password": password
        }

        factory = APIRequestFactory()
        request = factory.post(reverse('login'), body, format='json')

        response = LoginAPIView.as_view()(request)

        return response

    def create_strategy(symbol, body=None, user_id=None, token_access=None):

        if body is None:

            body = {
                'strategyNews': 'AlpacaLongETHUSD',
                'description': 'simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
                'user': user_id,
                'is_public': True,
                'is_active': True,
                'net_profit': 1.3,
                'percentage_profitable': 0.5,
                'max_drawdown': 3,
                'period': 'hour',
                'timer': '1',
            }

        body['symbol'] = symbol

        factory = APIRequestFactory()
        request = factory.post(reverse('createStrategy'), body, format='multipart',
                               HTTP_AUTHORIZATION='Bearer {}'.format(token_access))

        response = PostSettingAPIview.as_view()(request)

        create_trade_body = json.loads(response.data['tradingview']['message'])

        response.create_trade_body = create_trade_body

        return response

    def create_trading_config(strategy_id, broker_id, token_access, tradingConfigBody=None):

        # ? Only Long
        if tradingConfigBody == None:
            tradingConfigBody = {
                "strategyNews": strategy_id,
                "broker": broker_id,
                "quantityUSDLong": 5000,
                "useLong": True,
                "stopLossLong": -5,
                "takeProfitLong": 10,
                "consecutiveLossesLong": 3,
                "quantityUSDShort": 1,
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

        factory = APIRequestFactory()

        requests = factory.post(reverse('create_tradingValue'), tradingConfigBody, format='json',
                                HTTP_AUTHORIZATION='Bearer {}'.format(token_access))

        response = tradingConfigViews.as_view()(requests)

        return response

    def create_broker(token_access):

        bodyAlpaca = {
            "brokerName": "brokerAlpacaTest",
            "broker": "alpaca",
            "APIKeyID": settings.ALPACA_BROKER_TEST_API_KEY_ID,
            "SecretKey": settings.ALPACA_BROKER_TEST_SECRET_KEY,
            "isPaperTrading": True
        }

        factory = APIRequestFactory()

        request = factory.post(reverse('broker_alpaca'), bodyAlpaca, format='json',
                               HTTP_AUTHORIZATION='Bearer {}'.format(token_access))

        response = alpacaConfigurationSerializersView.as_view()(request)

        return response

    def get_broker(user_id, is_paper_trading=False):

        if is_paper_trading:
            broker_name = "alpacaTest"
        else:
            broker_name = "alpaca"

        broker_data = broker_model.objects.filter(
            owner_id=user_id, broker=broker_name)

        broker_count = broker_data.count()

        return broker_data

    def create_trade(body_token_strategy, trade_type='sell'):

        body_token_strategy['order'] = trade_type

        factory = APIRequestFactory()
        request = factory.post(
            reverse('trade_push_with_strategy'), body_token_strategy, format='json')

        response = strategyView.as_view()(request)

        return response

    def get_symbol(symbol):

        symbol_strategy = symbolStrategy.objects.get(
            Q(symbolName=symbol) | Q(symbolName_corrected=symbol)
        )

        return symbol_strategy