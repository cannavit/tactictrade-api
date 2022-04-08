from django.contrib import admin
from .models import *


class strategyNewAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'owner',
        'strategyNews',
        'symbol',
        'pusher',
        'is_public',
        'net_profit',
        'percentage_profitable',
        'max_drawdown',
        'period',
        'timer',
    ]

    # list_display = '__all__'

    pass


admin.site.register(strategyNews, strategyNewAdmin)

class symbolNameAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'symbolName',
        'symbolName_corrected',
        'url'
    ]


#     pass

admin.site.register(symbolStrategy,symbolNameAdmin)


# class followersAdmin(admin.ModelAdmin):

# list_display = [
#     "follower",
#     "strategy",
#     "ranking",
#     "is_active",
#     # "copy_maintainer_manual_outputs",
# ]

# pass


# admin.site.register(strategy_follower, followersAdmin)


# class commentsAdmin(admin.ModelAdmin):

#     list_display = [
#         'strategyNews',
#         'owner',
#         'message',
#         'create_at',
#         'like',
#         'dislike',
#     ]

#     pass


# admin.site.register(comments, commentsAdmin)
