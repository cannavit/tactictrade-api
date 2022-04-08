from apps.broker.api.views import (alpacaConfigurationSerializersView,
                                   brokerSerializersView)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.urls.resolvers import URLPattern

urlpatterns = [
    path('v1/all', brokerSerializersView.as_view(), name='broker'),
    path('v1/alpaca', alpacaConfigurationSerializersView.as_view(), name='broker_alpaca'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
