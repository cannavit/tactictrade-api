# APIs Configuration
from django.urls import path
from . import views

urlpatterns = [
    # Declarate path for the view tradingValueViews
    path('tradingvalues', views.trading_config_view.as_view(),
         name='create_tradingValue'),
    path('all', views.trading_config_get_all_view.as_view(), name='all'),
    path('tradingvalues/<slug:slug>',
         views.trading_config_slug_views.as_view(), name='tradingValue_edit'),
    path('strategy', views.strategy_view.as_view(),
         name='trade_push_with_strategy'),

]
