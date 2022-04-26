from django.db import models
from django.dispatch import receiver

from apps.authentication.models import User
# from apps.transaction.models import transactions as transactions_model

from django.db.models.signals import  pre_save
from django.dispatch import receiver
# Create your models here.

# import request libary
import requests
import json


from django.conf import settings
# Import django settings variables. 
# from apps.strategy

class devices(models.Model):

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE,null=False)
    token = models.CharField(max_length=255, blank=False, null=False, unique=False, default='')
    device_type = models.CharField(max_length=255, blank=False, null=False, unique=False, default='')

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.token


class notification(models.Model):

    NOTIFICATION_TYPE = [
        ('open_long_buy', 'open_long_buy'),
        ('close_long_sell', 'close_long_sell'),
        ('open_short_buy', 'open_short_buy'),
        ('open_short_sell', 'open_short_sell'),
    ]

    NAVIGATION_TYPE = [
        ('strategy', 'strategy'),
        ('news', 'news'),
        ('profile', 'profile'),
    ]

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE,null=False)
    transact_id = models.IntegerField(default=0, blank=False, null=False)

    notification =  models.CharField(
        choices=NOTIFICATION_TYPE, null=True, blank=True, max_length=60,)

    base_cost = models.FloatField(default=0, blank=False, null=False)
    base_price = models.FloatField(default=0, blank=False, null=False)



    title = models.CharField(max_length=100, blank=False, null=False, unique=False, default='')
    message = models.CharField(max_length=255, blank=False, null=False, unique=False, default='')
    priority = models.CharField(max_length=20, blank=False, null=False, unique=False, default='high')
    image = models.CharField(max_length=255, blank=False, null=False, unique=False, default='')
    symbol = models.CharField(max_length=20, blank=False, null=False, unique=False, default='')
    strategyName = models.CharField(max_length=40, blank=False, null=False, unique=False, default='')
    order = models.CharField(max_length=10, blank=False, null=False, unique=False, default='')
    operation = models.CharField(max_length=10, blank=False, null=False, unique=False, default='')

    profit = models.FloatField(default=0, blank=False, null=False)

    navigate_to = models.CharField(
        choices=NAVIGATION_TYPE, null=True, blank=True, max_length=60, default='')  

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_trade = models.BooleanField(default=False)
    is_winner = models.BooleanField(default=False)

    isClosed = models.BooleanField(default=False)


#     owner = models.ForeignKey(to=User, on_delete=models.CASCADE,null=False)


@receiver(pre_save, sender=notification)
def send_notification(sender, instance, *args, **kwargs):

    # Logic Message.     
    #! CREATED TRANSACTION
    if instance.id is None:
        # Fail of exist one open transaction
        
        send_notification = False
        if instance.notification == 'open_long_buy': 
            send_notification = True   

            instance.title = 'TacticTrade [' + instance.strategyName + '] ' + instance.operation + '/' + instance.order 
            instance.message = 'Trading: ' + instance.order + ' ' + instance.symbol + ',cost: ' + str(instance.base_cost) + '$, asset price ' + str(round(instance.base_price,3)) + '$'
            instance.navigate_to = ''
        
        devices_obj = devices.objects.filter(owner_id=instance.owner_id).values()
        if devices_obj.count() == 0:
            send_notification = False

        if send_notification:

            if devices_obj.count() == 1:
                token = devices_obj[0]['token']
            else:
                token = []
                for device in devices_obj:
                    token = token.append(device['token'])  
        
            body_firebase = {
                "notification": {
                    "body": instance.message,
                    "title": instance.title ,
                    "image": instance.image,
                },
                
                "priority": "high",
                "data": {
                    "type": instance.notification,
                },
                 "to": token
            }

            send_notification_firebase(body_firebase)

        if instance.notification == 'close_long_sell': 
            send_notification = True   

            instance.title = 'TacticTrade [' + instance.strategyName + '] ' + instance.operation + '/' + instance.order 
            instance.message = 'Close Trading: ' + instance.order + ' ' + instance.symbol + ',profit: ' + str(instance.profit) + '$, asset price ' + str(round(instance.base_price,3)) + '$'
            instance.navigate_to = ''
        
        devices_obj = devices.objects.filter(owner_id=instance.owner_id).values()
        if devices_obj.count() == 0:
            send_notification = False

        if send_notification:

            if devices_obj.count() == 1:
                token = devices_obj[0]['token']
            else:
                token = []
                for device in devices_obj:
                    token = token.append(device['token'])  
        
            body_firebase = {
                "notification": {
                    "body": instance.message,
                    "title": instance.title ,
                    "image": instance.image,
                },
                
                "priority": "high",
                "data": {
                    "type": instance.notification,
                },
                 "to": token
            }

            send_notification_firebase(body_firebase)


def send_notification_firebase(body_firebase):

    url = "https://fcm.googleapis.com/fcm/send"

    payload = json.dumps(body_firebase)

    headers = {
    'Authorization': 'key=' +  settings.PUSH_NOTIFICATIONS_FIREBASE_CLOUD_MESSAGE_TOKEN,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)