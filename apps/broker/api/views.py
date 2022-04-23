import alpaca_trade_api as tradeapi
from apps.authentication.models import User
from apps.broker.models import alpaca_configuration, broker
from apps.broker.utils.init_broker import InitData

# import settings in django
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response

from apps.broker.api.serializers import brokerSerializersOriginal, brokerSerializers, alpacaConfigurationSerializers


class brokerSerializersView(generics.ListAPIView):

    serializer_class = brokerSerializers
    queryset = broker.objects.all()
    permissions_class = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):

        if self.request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        # brokerbroker

        responseModel = self.queryset.filter(owner=self.request.user)

        values = responseModel.count()
        
        if responseModel.count() == 0:
            InitData.init_broker(self.request.user.id)
            responseModel = self.queryset.filter(owner=self.request.user)

        return responseModel


# Serializer alpacaConfigurationSerializers
# Model alpaca_configuration
# Using only CreateAPIView
class alpacaConfigurationSerializersView(generics.CreateAPIView):

    serializer_class = alpacaConfigurationSerializers
    queryset = alpaca_configuration.objects.all()
    permissions_class = (permissions.IsAuthenticated,)
    http_method_names = ['post', ]
    model = alpaca_configuration

    def post(self, request):

        if request.auth == None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = request.user.id
        data = request.data

        #! Check if exist one broker with the same name:
        exist_broker = broker.objects.filter(
            owner=userId, brokerName=request.data['brokerName']).count() > 0
        if exist_broker:
            return Response({
                "status": "error",
                "message": "The broker name already exist"
            }, status=status.HTTP_400_BAD_REQUEST)

        #! Check if is one test. Check if exit TEST_KEY
        try:
            TEST_KEY = data['TEST_KEY']
            if TEST_KEY == settings.TEST_KEY:
                TEST_KEY = True
                data['APIKeyID'] = settings.ALPACA_BROKER_TEST_API_KEY_ID
                data['SecretKey'] = settings.ALPACA_BROKER_TEST_SECRET_KEY
            else:
                TEST_KEY = False
        except KeyError:
            TEST_KEY = False

        tagPrice = 'Is a Paper Trading'

        if not data['isPaperTrading']:
            tagPrice = 'Is Real Trading'


        brokerExist = alpaca_configuration.objects.filter(
            APIKeyID=data['APIKeyID'],
            SecretKey=data['SecretKey']).count()

        if brokerExist > 0:
            return Response({
                "status": "error",
                "message": "Broker already exist"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create an Alpaca client
        # if TEST_KEY == False:

        try:
            api = tradeapi.REST(
                data['APIKeyID'], data['SecretKey'], 'https://paper-api.alpaca.markets')
        except Exception as e:
            return Response({
                "status": "error",
                "message": "The Alpaca broker data is invalid",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            Accountaccount = api.get_account()
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Invalid API Key or Secret Key",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        brokerResponse = broker.objects.create(
            owner_id=userId,
            capital=Accountaccount.cash,
            isPaperTrading=data['isPaperTrading'],
            broker=data['broker'],
            tagBroker='new',
            tagPrice=tagPrice,
            brokerName=data['brokerName'],
        )

        response = alpaca_configuration.objects.create(
            broker_id=brokerResponse.id,
            APIKeyID=data['APIKeyID'],
            SecretKey=data['SecretKey'],
            endpoint='https://paper-api.alpaca.markets'
        )

        # Print Account Detailsprint(account.id, account.equity, account.status)

        return Response({
            "status": "success",
            "message": "Alpaca Configuration Created",
            # "response": response,
            "results": {
                "id": brokerResponse.id,
                "capital": brokerResponse.capital,
                "create_at": brokerResponse.create_at,
                "updated_at": brokerResponse.updated_at,
                "broker": brokerResponse.broker,
                "tagBroker": brokerResponse.tagBroker,
                "isActive": brokerResponse.isActive,
                "block_is_active": brokerResponse.block_is_active,
                "brokerName": brokerResponse.brokerName,
                "urlLogo": brokerResponse.urlLogo,
                "owner": brokerResponse.owner.id,
                "broker_configration_id": response.id,
            }
        }, status=status.HTTP_201_CREATED)
