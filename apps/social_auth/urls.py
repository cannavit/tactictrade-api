from django.urls import path
from django.urls.resolvers import URLPattern
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('google_login/', GoogleSocialAuthView.as_view(), name='google_login'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


