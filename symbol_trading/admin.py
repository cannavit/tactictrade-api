from django.contrib import admin

# Register your models here.
from .models import symbol


class symbolNameAdmin(admin.ModelAdmin):

    list_display = [
        'symbolName',
        'image',
    ]


    pass

admin.site.register(symbol,symbolNameAdmin)