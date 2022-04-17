from cmath import log
from django.contrib import admin

# Register your models here.



from .models import alpaca_configuration
admin.site.register(alpaca_configuration)



from .models import broker

class brokerAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'owner',
        'capital',
        'isPaperTrading',
        'broker',
        
    ]

admin.site.register(broker, brokerAdmin)
