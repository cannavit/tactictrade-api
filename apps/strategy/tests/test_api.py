import json
import random
import string

import requests
from apps.authentication.api.serializers import (LoginSerializer,
                                            RegisterSerializer,
                                            UserSocialSerializer)

                                            
from apps.authentication.models import User
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import (APIClient, APIRequestFactory, APITestCase,
                                 force_authenticate)
from apps.strategy.api.views import PostSettingAPIview
from utils.by_tests.select_test_material import trading_random_image


# Create test for createStrategy
class TestCreateStrategy(APITestCase):

    def setUp(self):

        # Create random name and email
        self.name = ''.join(random.choice(string.ascii_uppercase +
                                          string.digits) for _ in range(10))

        self.email = ''.join(random.choice(string.ascii_uppercase + string.digits)
                             for _ in range(10)) + '@test.com'

        user = User.objects.create_user(
            username=self.name,
            email=self.email,
            password='Passw0rd!'
        )

        # active and verify the user 
        user.is_active = True
        user.is_verified = True
        user.save()

        self.user = user

        # Login user 
        body = {
                    'email': self.email,
                    'password': 'Passw0rd!',
                }
           
    
        response = self.client.post(reverse('login'), body)      

        token_access = response.data['token_access']

        print("TOKEN : ", token_access)
        self.token_access = token_access
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.body = {
            'strategyNews': 'StrategyTestV2',
            'description': 'simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
            'user': user.id,
            # is_public
            'is_public': True,
            # is_active
            'is_active': True,
            # net_profit
            'net_profit': 1.3,
            # percentage_profitable
            'percentage_profitable': 0.5,
            # max_drawdown  
            'max_drawdown': 3,
            # period
            'period': 'hour',
            # timer
            'timer': '1',
            # 'upload_file': upload_file,
        }


    def test_create_strategy_without_picture(self):

        symbol = 'ETHUSD'
        self.body['symbol'] = symbol

        factory = APIRequestFactory()
        request = factory.post(reverse('createStrategy'), self.body, format='multipart',
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_access))
        
        view = PostSettingAPIview.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_create_strategy_with_picture(self):

        # From data. 
        data = File(open('utils/by_tests/tests_material/trading_images/MSFT.png', 'rb'))
        upload_file = SimpleUploadedFile('MSFT.png', data.read(),content_type='multipart/form-data')
        
        symbol = 'MSFT'
        self.body['symbol'] = symbol
        # self.body['post_image'] = upload_file.read()
        self.body['post_image'] = upload_file



        factory = APIRequestFactory()
        request = factory.post(reverse('createStrategy'), self.body, format='multipart',
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_access))
        
        view = PostSettingAPIview.as_view()

        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']

        # Create one request to url data['url_new'] and check the statuscode 200 use the library requests
        urlImage = data['url_new']
        responseImage = requests.get(urlImage)
        self.assertEqual(responseImage.status_code, 200)
        
        self.response = response
        self.data = data

