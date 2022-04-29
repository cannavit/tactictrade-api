from django.db import models
from apps.authentication.models import User
from apps.strategy.models import strategyNews
# Create your models here.s

class setting(models.Model):

    CATEGORY_SETTINGS = [
        ('Receive Long Notifications Push', 'notifications_push_long'),
        ('Receive Short Notifications Push', 'notifications_push_short'),
        ('language', 'Language'),
        ('TestOption', 'Test Option'),        

    ]

    FAMILY_SETTINGS = [
        ('Notifications', 'notifications'),
        ('Test', 'test'),

    ]
    
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    setting  = models.CharField(choices=CATEGORY_SETTINGS,null=False,blank=False,max_length=100, unique=True)
    family = models.CharField(choices=FAMILY_SETTINGS,null=False,blank=False,max_length=100)

    is_active = models.BooleanField(default=True)

    bool_value = models.BooleanField(default=True)
    string_value = models.CharField(max_length=100, null=True, blank=True)

    # https://api.flutter.dev/flutter/material/Icons-class.html
    icon = models.CharField(max_length=30, null=True, blank=True, default='0xf03c3')

    is_switch_on = models.BooleanField(default=True)

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.owner.email


# class functionalities(models.Model):
    
#     functionality  = models.CharField(choices=CATEGORY_FUNCTIONALITIES,null=False,blank=False,max_length=100, unique=True)
#     family = models.CharField(choices=FAMILY_FUNCTIONALITIES,null=False,blank=False,max_length=100)

#     is_active = models.BooleanField(default=True)

#     bool_value = models.BooleanField(default=True)
#     string_value = models.CharField(max_length=100, null=True, blank=True)

#     # https://api.flutter.dev/flutter/material/Icons-class.html
#     icon = models.CharField(max_length=30, null=True, blank=True, default='0xf03c3')

#     is_switch_on = models.BooleanField(default=True)

#     create_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


#     def __str__(self):
#         return self.owner.email