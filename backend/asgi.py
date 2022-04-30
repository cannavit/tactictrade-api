import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from channels.routing import URLRouter

from apps.asset.routing import ws_urlpatterns as ws_asset_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.

application = ProtocolTypeRouter({
    "http":  get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(
        ws_asset_urlpatterns
    ))
})