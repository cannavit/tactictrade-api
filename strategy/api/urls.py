from django.urls import path
from django.urls.resolvers import URLPattern
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('v1/all', SettingsAPIview.as_view(), name='allStrategies'),
    path('v1/add', PostSettingAPIview.as_view(), name='createStrategy'),
    path('v1/put/<int:pk>', PutSettingAPIview.as_view(), name='putStrategy'),
    # path('v1/owner', GetStrategiesOwner.as_view(), name='ownerStrategies'),
    path('v1/social/<int:pk>', PutStrategySocialAPIview.as_view(), name='socialStrategies'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

