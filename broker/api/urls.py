from django.urls import path
from django.urls.resolvers import URLPattern
from broker.api.views import brokerSerializersView, alpacaConfigurationSerializersView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('v1/all', brokerSerializersView.as_view(), name='broker'),
    path('v1/alpaca', alpacaConfigurationSerializersView.as_view(), name='broker_alpaca'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)