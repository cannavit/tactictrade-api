from django.contrib             import admin
from .models import setting
admin.site.site_header = 'TacticTrade-Api'

class settingAdmin(admin.ModelAdmin):

    list_display = [
            'owner',
            'theme',
            'language',
            'notifications_push_long',
            'notifications_push_short',
        ]
        
    pass


admin.site.register(setting,settingAdmin)

# Register trading_config
# class trading_configAdmin(admin.ModelAdmin):
    # List_display all data
