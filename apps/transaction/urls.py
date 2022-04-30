# APIs Configuration
from django.urls import path
from . import views

urlpatterns = [
    # Declarate path for the view tradingValueViews
    path('opens', views.TransactionsView.as_view(), name='transactions_opens'),
    path('close_manual/<int:pk>', views.closeTransactionsView.as_view(), name='closeManual'),
    path('records/<int:pk>/<slug:private>', views.TransactionRecordsView.as_view(), name='closeManual'),

]
# closeTransactionsView