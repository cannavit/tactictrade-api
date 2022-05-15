# APIs Configuration
from django.urls import path
from . import views

urlpatterns = [
    # Declarate path for the view tradingValueViews
    path('tradingvalues', views.trading_config_view.as_view(),
         name='create_tradingValue'),
         
    path('view_flutter/<int:pk>', views.trading_config_flutter_view.as_view(),
         name='view_flutter'),

    path('all', views.trading_config_get_all_view.as_view(), name='all'),
    path('tradingvalues/<slug:slug>',
         views.trading_config_slug_views.as_view(), name='tradingValue_edit'),
    path('strategy', views.strategy_view.as_view(),
         name='trade_push_with_strategy'),

    path('openlong/<int:pk>', views.tradingOpenLongView.as_view(), name='trading_open_long'),
    path('openshort/<int:pk>', views.tradingOpenShortView.as_view(), name='trading_open_short'),

]
