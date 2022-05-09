import json
import re
import secrets

from apps.authentication.models import User
from apps.broker.models import broker as broker_model
from apps.broker.utils.init_data import InitData
from apps.strategy.api.serializers import (CreateSettingSerializers,
                                           OwnerStrategySerializers,
                                           PutSettingSerializers,
                                           PutStrategySocialSerializers,
                                           SettingsSerializers,
                                           SettingsSerializersPost)
from apps.strategy.models import strategyNews, symbolStrategy
from django.conf import settings
from django.core.files import File
from django.db.models import Q
from django.views.generic import DetailView
from django_filters.rest_framework import DjangoFilterBackend
from drf_multiple_model.views import ObjectMultipleModelAPIView
from requests import patch
from rest_framework import filters, generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from utils.create_bot_by_new_strategy import create_bot_by_new_strategy
from utils.upload.imagekit import upload_image_imagekit

from ..utils import get_symbolName


class SettingsAPIview(generics.ListAPIView):

    serializer_class = SettingsSerializers
    queryset = strategyNews.objects.all()
    filter_backends = [DjangoFilterBackend]
    permissions_classes = (permissions.IsAuthenticated,)
    
    filterset_fields = ['id', 'strategy_token', 'is_public']

    def get_queryset(self): 
        #TODO this control not work with swagger view.  (Fix it)

        user = self.request.user
        self.user_id = user.id

        category = self.request.query_params.get('category', None)

        if category == 'me':
            results = strategyNews.objects.filter(owner_id=user.id).order_by('-id')
        elif category == 'favorite':
            results = strategyNews.objects.filter(owner_id=user.id,favorite__in=[user.id]).order_by('-id')
        elif category == 'likes':
            results = strategyNews.objects.filter(owner_id=user.id,likes__in=[user.id]).order_by('-id')            
        elif category == 'winners':
            # TODO Create logic for filter by winners strategies. 
            results = strategyNews.objects.filter(Q(owner_id=user.id) | Q(is_public__in=[True])).order_by('-id')
        elif category == 'top_short':
            # TODO Create logic for filter by top_short strategies. 
            results = strategyNews.objects.filter(Q(owner_id=user.id) | Q(is_public__in=[True])).order_by('-id')
        elif category == 'top_long':
            # TODO Create logic for filter by top_long strategies. 
            results = strategyNews.objects.filter(Q(owner_id=user.id) | Q(is_public__in=[True])).order_by('-id')
        elif category == 'all' or category == None:
            # TODO Create logic for filter by top_long strategies. 
            results = strategyNews.objects.filter(Q(owner_id=user.id) | Q(is_public__in=[True])).order_by('-id')

        return results


class PostSettingAPIview(generics.CreateAPIView):

    serializer_class = CreateSettingSerializers

    queryset = strategyNews.objects.all()
    permissions_class = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['post', ]
    model = strategyNews

    def post(self, request):

        if request.auth == None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create random token
        userId = request.user.id

        # Check if exist one strategy with the same name and user. 
        exist_strategy = strategyNews.objects.filter(owner_id=userId, strategyNews=request.data['strategyNews']).count() > 0

        if exist_strategy:
            return Response({
                "status": "error",
                "message": "You have one strategy with the same name. "
            }, status=status.HTTP_400_BAD_REQUEST)

        # try:
        if True:

            symbolResponse = get_symbolName(request.data['symbol'])

            if symbolResponse['error'] == True:
                return Response({
                    "status": "error",
                    "message": symbolResponse['message']
                }, status=status.HTTP_400_BAD_REQUEST)

            haveImage = False
            try:
                if request.data['post_image']:
                    post_image = request.data['post_image']
                    del request.data['post_image']
                    haveImage = True
            except:
                print('not image included')

            data = json.dumps(request.data)
            data = json.loads(data)

            if data['strategyNews']:
                data['strategyNews'] = request.data['strategyNews'].capitalize()

            data['symbol_id'] = symbolResponse['symbol_id']
            data['owner_id'] = userId

            data['strategy_token'] = secrets.token_hex(24)

            if data['is_public']:
                data['is_public'] = bool(data['is_public'])

            if data['is_active']:
                data['is_active'] = bool(data['is_active'])

            data['pusher'] = 'https://s3.tradingview.com/userpics/6171439-Hlns_big.png'

            # data['id'] =

            # ? Remove data from request
            del data['symbol']

            try:
                del data['user']
            except:
                pass

            if haveImage == True:

                try:
                    strategyNews.objects.create(
                        **data,
                        post_image=post_image
                    )
                except Exception as e:
                    return Response({
                        "status": "error",
                        "message": "The strategy name need to be unique"
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)

                # Save the image inside of the imagekit.io
                dataStrategy = strategyNews.objects.filter(
                    strategy_token=data['strategy_token']).values()[0]

                url_new = upload_image_imagekit(dataStrategy['post_image'])

                strategyNews.objects.filter(id=dataStrategy['id']).update(
                    post_image="",
                    url_image=url_new['url']
                )

                data['url_new'] = url_new['url']
                data['strategyNewsId'] = dataStrategy['id']

            else:

                dataStrategy = strategyNews.objects.create(
                    **data
                )

                data['strategyNewsId'] = dataStrategy.id

            text1 = '''{
                "strategy": "''' + str(data['strategyNews']) + '''",
                "token": "''' + str(data['strategy_token']),

            text2 = '''",
                    "order": "{{strategy.order.action}}",
                    "contracts": "{{strategy.order.contracts}}",
                    "ticker": "{{ticker}}",
                    "position_size": "{{strategy.position_size}}"
                }'''

            TradingViewMessageBody = re.sub(' +', ' ', text1[0] + text2)
            TradingViewWebHook = settings.BASE_URL + "/trading/strategy"

            # ? initialize  the broker
            if not broker_model.objects.filter(owner_id=userId,broker='paperTrade').exists():
                InitData.init_broker(userId)

            #! Create bot strategy --->
            create_bot_by_new_strategy(
                dataStrategy, symbolResponse['symbolName'])

            return Response({
                "status": "success",
                "message": "Strategy created successfully",
                "data": data,
                "tradingview": {
                    "message": TradingViewMessageBody,
                    "webhook": TradingViewWebHook
                }
            })

        # except Exception as e:
        #     return Response({
        #         "status": "error",
        #         "message": "Not found the field: " + str(e)
        #     }, status=status.HTTP_400_BAD_REQUEST)


class PutSettingAPIview(generics.UpdateAPIView):

    serializer_class = PutSettingSerializers
    queryset = strategyNews.objects.all()
    permissions_class = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]


class GetSettingsAPIview(generics.ListAPIView):

    serializer_class = SettingsSerializers
    queryset = strategyNews.objects.all()
    permissions_class = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ['id', 'strategy_token', 'is_public']
    search_fields = ['id', 'strategy_token', 'is_public']

    def get_queryset(self):

        if self.request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Todo use the is_public = True
        return strategyNews.objects.filter(owner=self.request.user.id)


class StrategiesListAPIView(ObjectMultipleModelAPIView):

    pagination_class = None

    querylist = [
        {
            'queryset': strategyNews.objects.all(), 'serializer_class': SettingsSerializers
        },
        {
            'queryset': User.objects.all(), 'serializer_class': OwnerStrategySerializers
        }
    ]


# TODO get all Owner strategies
class GetStrategiesOwner(generics.ListAPIView):

    serializer_class = SettingsSerializers
    queryset = strategyNews.objects.all()
    permissions_class = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ['id', 'strategy_token', 'is_public']
    search_fields = ['id', 'strategy_token', 'is_public']

    def get_queryset(self):

        if self.request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Todo use the is_public = True
        return strategyNews.objects.filter(owner=self.request.user.id)


class PutStrategySocialAPIview(generics.UpdateAPIView):

    serializer_class = PutStrategySocialSerializers
    queryset = strategyNews.objects.all()
    permissions_class = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):

        if self.request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = request.user.id
        body = request.data
        strategyId = self.kwargs['pk']

        strategy = strategyNews.objects.filter(id=strategyId)

        if strategy.count() == 0:
            return Response({
                "status": "error",
                "message": "Strategy not found"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Logic for likes.
        if 'likes' in body:
            if body['likes'] == True:
                if strategyNews(id=strategyId).likes.filter(id=userId).count() == 0:
                    strategyNews(id=strategyId).likes.add(userId)
            else:
                if strategyNews(id=strategyId).likes.filter(id=userId).count() > 0:
                    strategyNews(id=strategyId).likes.remove(userId)

        # Logic for favorite
        if 'favorite' in body:
            if body['favorite'] == True:
                if strategyNews(id=strategyId).favorite.filter(id=userId).count() == 0:
                    strategyNews(id=strategyId).favorite.add(userId)
            else:
                if strategyNews(id=strategyId).favorite.filter(id=userId).count() > 0:
                    strategyNews(id=strategyId).favorite.remove(userId)

        # Logic for follower
        if 'followers' in body:
            if body['followers'] == True:
                if strategyNews(id=strategyId).followers.filter(id=userId).count() == 0:
                    strategyNews(id=strategyId).followers.add(userId)
            else:
                if strategyNews(id=strategyId).followers.filter(id=userId).count() > 0:
                    strategyNews(id=strategyId).followers.remove(userId)

        # Respose with code 200
        return Response({
            "status": "success",
            "message": "Strategy updated successfully"
        }, status=status.HTTP_200_OK)

        # print(userId)
