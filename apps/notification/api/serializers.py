from email.policy import default
from rest_framework import serializers
from apps.authentication.models import User, followers_mantainers
from apps.strategy.models import strategyNews, symbolStrategy
from apps.authentication.models import User
from django.conf import settings

from apps.notification.models import devices

class DevicesSerializers(serializers.ModelSerializer):

    class Meta:

        model = devices
        fields = [
            'token',
            'device_type'
        ]

        