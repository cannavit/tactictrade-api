from django.contrib import admin
from .models import trading_config
# from .models import trading_parameters
# Register your models here.

# admin.site.register(trading_parameters)


# Define Admin table view
class trading_configAdmin(admin.ModelAdmin):
    
    # owner
    # strategyNews
    # broker
    # quantityUSDLong

    list_display = [
        'id',
        'owner',
        'strategyNews',
        'broker',
        'is_active_short',
        'is_active_long'

    ]



admin.site.register(trading_config,trading_configAdmin)
