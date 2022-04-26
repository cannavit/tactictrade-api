from django.urls import path
from django.urls.resolvers import URLPattern
from django.conf.urls.static import static
from django.conf import settings

from apps.notification.api.views import NotificationAPIview

urlpatterns = [
    path('v1/register', NotificationAPIview.as_view(), name='register_or_create_notification_token'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

