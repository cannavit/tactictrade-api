import json
import random
import string

from apps.authentication.api.serializers import (LoginSerializer,
                                                 RegisterSerializer,
                                                 UserSocialSerializer)
from apps.authentication.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


# Create test for RegisterSerializer
class RegisterSerializerTest(APITestCase):

    def test_register_user(self):

        # Create random name and email
        name = ''.join(random.choice(string.ascii_uppercase +
                       string.digits) for _ in range(10))
        email = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(10)) + '@test.com'
        
        body = {
            'username': name,
            'email': email,
            'password': 'Passw0rd!',
        }

        response = self.client.post(reverse('register_new_user'), body)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# Create test for the LoginSerializer 
class LoginSerializerTest(APITestCase):
    
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

        def test_login_user_not_verified(self):
                
                body = {
                    'email': self.email,
                    'password': 'Passw0rd!',
                }
           
    
                response = self.client.post(reverse('login'), body)  
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        def test_login_user_verified(self):

                body = {
                    'email': self.email,
                    'password': 'Passw0rd!',
                }

                # Modify the field is_verified to True
                user = User.objects.get(email=self.email)
                user.is_verified = True
                user.save()

                response = self.client.post(reverse('login'), body)  

                print("response: ", response)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                # Save token value from request
                # self.token = response.data['token']

                # Check if token is valid 
                # self.assertIsNotNone(self.token)







            

