from django.db import models
from authentication.models import User
from strategy.models import strategyNews
# Create your models here.s

class setting(models.Model):

    CATEGORY_THEMES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]

    CATEGORY_SETTINGS = [
        ('theme', 'Theme'),
        ('generals', 'General'),
    ]

    LANGUAGE_SETTINGS = [
        ('es', 'ES'),
        ('en', 'EN'),
        ('fr', 'FR'),
        ('de', 'DE'),
        ('it', 'IT'),
        ('pt', 'PT'),
        ('ru', 'RU'),
        ('zh', 'ZH'),
    ]    


    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    setting     = models.CharField(choices=CATEGORY_SETTINGS,default='generals',max_length=60,unique=False)
    theme  = models.CharField(choices=CATEGORY_THEMES,default='light',null=True,blank=True,max_length=60)
    language    = models.CharField(choices=LANGUAGE_SETTINGS,default='en',blank=False,max_length=20)

    def __str__(self):
        return self.setting
