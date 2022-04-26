import json
import re
import secrets

from apps.authentication.models import User
from apps.broker.models import broker as broker_model
from apps.broker.utils.init_broker import InitData
from apps.notification.api.serializers import DevicesSerializers
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
from utils.convert_json_to_objects import convertJsonToObject
from utils.create_bot_by_new_strategy import create_bot_by_new_strategy

from apps.notification.models import devices

class NotificationAPIview(generics.CreateAPIView):

    serializer_class = DevicesSerializers
    queryset = devices.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)


    def post(self, request):

        if request.auth == None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create random token
        userId = request.user.id

        data = convertJsonToObject(request.data)

        try:
            device_obj = devices.objects.get(owner_id=userId, token=data.token)
            message = "Token already exists"
        except Exception as e:
            message = "Token created"
            device_obj = devices.objects.create(owner_id=userId, token=data.token, device_type=data.device_type)


        return Response({
            "status": "success",
            "message": message,
            "data": {
                "token": device_obj.token,
                "device_type": device_obj.device_type
            }
        }, status=status.HTTP_200_OK)
