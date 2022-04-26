from django.contrib import admin
from apps.notification.models import devices
# Register your models here.
class deviceAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'owner',
        'device_type',
        'token',
        
    ]

admin.site.register(devices, deviceAdmin)