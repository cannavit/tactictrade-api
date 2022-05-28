from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt import views as jwt_views
from drf_yasg2.views import get_schema_view as get_schema_view2
from drf_yasg2 import openapi
from django.conf.urls.static import static
from django.conf import settings


schema_view = get_schema_view2(
    openapi.Info(
        title="TacticTrade [Api Docs]",
        default_version='v1',
    ),
    public=True,
)



# ROUTER LIST
router = routers.DefaultRouter()
# router.register('user', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('settings/', include('setting.api.urls')),
    path('account/', include('apps.authentication.api.urls')),
    path('trading/', include('apps.trading.urls')),
    path('strategy/', include('apps.strategy.api.urls')),
    path('broker/', include('apps.broker.api.urls')),
    path('social_auth/', include('apps.social_auth.urls')),
    path('transactions/', include('apps.transaction.urls')),
    path('notifications/', include('apps.notification.api.urls')),
    path('settings/', include('apps.setting.api.urls')),
    path('market_data/', include('apps.market_data.api.urls')),




    path('', include(router.urls)),
    path('api_schema/', get_schema_view(title='TacticTrade Apis',
         description='REST API Documentation'), name='api_schema'),
    path('docs/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),


]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
