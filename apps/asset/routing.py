from django.urls import path 
from .consumers import WSConsumer

ws_urlpatterns = [
    path('ws/asset', WSConsumer.as_asgi(), name='ws_assets'),
]