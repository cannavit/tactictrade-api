from django.contrib import admin
from apps.transaction.models import transactions
# Register your models here.

# Define orders transactions
class transactionsAdmin(admin.ModelAdmin):

    list_display = ('id','isClosed','owner', 'strategyNews', 'broker', 'symbol', 'is_winner','is_paper_trading', 'order', 'operation','spread',
     'qty_open', 'amount_open',  'price_open',   'base_cost',
     'qty_close','amount_close', 'price_closed', 'close_cost', 
     'profit', 'profit_percentage','stop_loss', 'take_profit', 'status')
    
    # list_filter = ( 'strategyNews', 'broker', 'symbol', 'is_paper_trading', 'order', 'operation',    'isClosed',  'is_winner')
    # search_fields = ('strategyNews', 'broker', 'symbol', 'is_paper_trading', 'order', 'operation',   'isClosed',  'is_winner')

admin.site.register(transactions,transactionsAdmin)
    