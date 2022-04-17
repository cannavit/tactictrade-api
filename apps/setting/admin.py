from django.contrib             import admin
from .models import setting
admin.site.site_header = 'TacticTrade-Api'

class settingAdmin(admin.ModelAdmin):
    # list_display = ['setting','theme', 'language']
    pass

admin.site.register(setting,settingAdmin)

# Register trading_config
# class trading_configAdmin(admin.ModelAdmin):
    # List_display all data
