# APIs Configuration
from django.urls import path
from . import views

urlpatterns = [
    # Declarate path for the view tradingValueViews
    path('tradingvalues', views.tradingConfigViews.as_view(),
         name='create_tradingValue'),
    path('all', views.tradingConfigGetAllViews.as_view(), name='all'),
    path('tradingvalues/<slug:slug>',
         views.tradingConfigSlugViews.as_view(), name='tradingValue_edit'),
    path('strategy', views.strategyView.as_view(), name='trade_push_with_strategy'),

]
