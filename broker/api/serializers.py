from email.policy import default
from rest_framework import serializers
from authentication.models import *
from ..models import *
from authentication.models import User
from django.conf import settings


class brokerSerializersOriginal(serializers.ModelSerializer):

    class Meta:
        
        model  = broker
        fields = '__all__'


class brokerSerializers(serializers.ModelSerializer):

    class Meta:
        model  = broker
        fields = '__all__'


    def to_representation(self, instance):
        
        response = super().to_representation(instance)

        response['capital'] = round(instance.capital,1)
            
        return response



class alpacaConfigurationSerializers(serializers.ModelSerializer):


    brokerName = serializers.CharField(required=True)
    broker = serializers.CharField(required=True)
    APIKeyID = serializers.CharField(required=True)
    SecretKey = serializers.CharField(required=True)
    isPaperTrading = serializers.BooleanField(required=True)

    class Meta:
        model  = alpaca_configuration

        fields = [
            'brokerName',
            'broker',
            'APIKeyID',
            'SecretKey',
            'isPaperTrading',
        ]

