from django.contrib             import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    # 
    list_display = ['id', 'username','email','is_active','is_staff','is_verified', 'is_bot']
    
    pass

admin.site.register(User,UserAdmin)



# class FlollowersAdmin(admin.ModelAdmin):
#     # list_display = ['user_id','following_user_id','created']

    
#     pass


admin.site.register(followers_mantainers)