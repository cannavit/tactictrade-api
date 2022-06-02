import ast
import datetime
import jwt
from apps.authentication.models import User, followers_mantainers
from apps.authentication.utils import Util
from apps.broker.utils.init_data import InitData

from asgiref.sync import sync_to_async
# Import settings
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from utils.market_data.import_data import import_data_market, import_data_ticket
from utils.upload.imagekit import upload_image_imagekit
from apps.authentication.api.serializers import FollowingSerializer, RegisterSerializer, EmailVerificationSerializer, UserSerializer, LoginSerializer, ProfileSerializers
import yfinance as yf

from apps.transaction.models import transactions
from apps.strategy.models import symbolStrategy

from django.db.models import Q


# PERIOD:
# Range of time for read 
# INTERVAL: row size of data

# Example: 
# Get one month of data with interval of 30min
# /AAPL/1mo/30m

class YahooFinView(generics.GenericAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def get(self, request, symbolName, period, interval, strategy):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        # if symbol, interval, days are null then return error
        if symbolName is None or period is None or interval is None or strategy is None:
            return Response({"error": "symbol, period, days are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            symbol_strategy = symbolStrategy.objects.get(
                Q(symbolName=symbolName) | Q(symbolName_corrected=symbolName)
            )
        except Exception as e:
            return Response({"error": "symbol not found"}, status=status.HTTP_400_BAD_REQUEST)

        #TODO create pages filter
        # Import data from Yahoo Finance
        data_json = import_data_ticket(ticker=symbol_strategy.symbolName_corrected, period=period, interval=interval).download()
        

        #TODO optimize the response
        transaction_list =  transactions.objects.filter(strategyNews_id=int(strategy)).values_list("id",  "operation", "create_at", "close_at" )

        # .filter(symbol_id=symbol_strategy.id)

        # .filter(strategyNews_id=int(strategy))


        # Create 
        return Response({
            "status": "success",
            "results": data_json,
            "operations": transaction_list
        })


        



        
