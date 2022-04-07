from os import access
import random
from rest_framework.exceptions import AuthenticationFailed
from authentication.models import User
from django.conf import settings
from django.contrib import auth
from authentication.api.serializers import UserSerializer, RegisterSerializer, UserSocialSerializer


def generate_username(name, email):

    username = "".join(name.split(' ')).lower()

    if User.objects.filter(email=email).exists():
        return username
    else:
        random_username = username + str(random.randint(1, 100))

        return random_username


def register_social_user(provider, user_id, email, name, picture):

    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        userOwner = filtered_user_by_email.values()[0]

        if provider == userOwner['auth_provider']:

            new_user = auth.authenticate(
                email=email,
                password=settings.SOCIAL_SECRET
            )

            token = new_user.tokens()

            return {
                'email': new_user.email,
                'username': new_user.username,
                'token_refresh': token['refresh'],
                "token_access": token['access']
            }


        else:
            raise AuthenticationFailed(
                detail='Please login with your existing account ' +
                filtered_user_by_email[0].auth_provider
            )

    else:

        serializer = UserSerializer(data={
            'password': settings.SOCIAL_SECRET,
            'email': email,
        })

        if serializer.is_valid():
            serializer.save()

            nameList = name.split(' ')

            user = {
                'username': generate_username(email[0:email.find('@')], email),
                'first_name': nameList[0],
                'last_name': nameList[1],
                'auth_provider': provider,
                'url_picture': picture,
            }

            userObjects = User.objects.filter(email=email).values()[0]
            
            User.objects.filter(
                id=userObjects['id']).update(**user)

            new_user = auth.authenticate(
                email=email,
                password=settings.SOCIAL_SECRET
            )
            token = new_user.tokens()

            return {
                'email': new_user.email,
                'username': new_user.username,
                'token_refresh': token['refresh'],
                "token_access": token['access']
            }
