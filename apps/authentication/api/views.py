# from django.contrib.auth.models import User
import ast
import json
import os

import jwt
import requests
from apps.authentication.models import User, followers_mantainers
from apps.authentication.utils import Util
from apps.broker.utils.init_broker import InitData

from asgiref.sync import sync_to_async
# Import settings
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, views, viewsets

from rest_framework.parsers import FormParser, MultiPartParser

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from utils.upload.imagekit import upload_image_imagekit

from apps.authentication.api.serializers import FollowingSerializer, RegisterSerializer, EmailVerificationSerializer, UserSerializer, LoginSerializer, ProfileSerializers

class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class RegisterViewSet(generics.GenericAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny, )

    def post(self, request):

        user = request.data

        try:
            MASTER_KEY = request.data['MASTER_KEY']
        except:
            MASTER_KEY = None

        try:
            TEST_KEY = request.data['TEST_KEY']
        except:
            TEST_KEY = None

        if MASTER_KEY == settings.MASTER_KEY:

            user['is_staff'] = True
            user['is_active'] = True
            user['is_verified'] = True

            del user['MASTER_KEY']
        elif TEST_KEY == settings.TEST_KEY:
            user['is_staff'] = False
            user['is_active'] = True
            user['is_verified'] = True
            del user['TEST_KEY']
        else:
            user['is_staff'] = False
            user['is_active'] = False
            user['is_verified'] = False

        serializer = self.serializer_class(data=user)

        if serializer.is_valid(raise_exception=True):

            user_serializer = serializer.save()
            user_data = serializer.data

            # Create Token for validate the user:
            user = User.objects.get(email=user_data['email'])

            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relative_link = reverse('email-verify')
            absurl = 'http://' + current_site + \
                relative_link + '?token=' + str(token)

            email_body = absurl

            data = {
                'email_body': email_body,
                'email_subject': 'Verify your email address',
                'to_email': user.email,
                'absurl': absurl
            }

            # Util.send_email(data)
            # Async send email service
            sync_to_async(Util.send_email(data))

            #! Initial user data
            InitData.init_broker(user.id)
            return Response(user_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(views.APIView):

    serializer_class = EmailVerificationSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny, )

    # token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Token', type=openapi.TYPE_STRING)
    # @swagger_auto_schema( manual_parameters=['token_param_config'])
    user_response = openapi.Response(
        'response description', EmailVerificationSerializer)
    test_param = openapi.Parameter(
        'token', openapi.IN_QUERY, description="Add Token email sended", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[test_param], responses={200: user_response})
    def get(self, request):
        token = request.GET.get('token')

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])

            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({
                'message': 'Successfully verified',
                'email': user.email
            }, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as indentifier:
            return Response({'error': 'Token is expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError as identifier:
            return Response({'error': 'Token is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)


class UserCreate(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )

    # def post(self, request):
    # print("@Note-01 ---- -1871608462 -----")


class LoginAPIView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.data['tokens']

        # Convert string to json
        tokensJson = ast.literal_eval(tokens)
        token_access = tokensJson['access']
        token_refresh = tokensJson['refresh']

        return Response({'token_refresh': token_refresh, 'token_access': token_access}, status=status.HTTP_200_OK)


username_input = openapi.Parameter(
    'username', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
about_input = openapi.Parameter(
    'about', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
profile_image_input = openapi.Parameter(
    'profile_image', in_=openapi.IN_QUERY, type=openapi.TYPE_FILE)
# is_public_input = openapi.Parameter(
#     'is_public', in_=openapi.IN_QUERY, type=openapi.T)


class profileViews(generics.GenericAPIView):

    serializer_class = User
    queryset = User.objects.all()
    permissions_classes = (permissions.IsAuthenticated,)

    def get(self, request):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = request.user.id
        data = User.objects.filter(id=userId).values()[0]

        reponse = {
            "profile_image":  settings.MEDIA_URL + data['profile_image'],
            "username": data['username'],
            "about": data['about'],
            'is_public': data['is_public'],

        }

        return Response(reponse, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[username_input, about_input,
                           profile_image_input],
    )
    def put(self, request, *args, **kwargs):

        if request.auth == None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        body = request.data

        namespace = request.data['namespace']
        about = request.data['about']
        profile_image = request.data['profile_image']
        userId = request.user.id

        User.objects.filter(id=userId).update(
            username=namespace, about=about, profile_image=profile_image)

        return Response({
            "status": "success",
            "message": "Profile updated successfully"
        }, status=status.HTTP_200_OK)


class ProfileListAPIview(generics.UpdateAPIView):

    serializer_class = ProfileSerializers
    queryset = User.objects.all()
    permissions_class = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        body = request.data

        user = User.objects.get(id=request.user.id)

        serializer = ProfileSerializers(user, data=request.data)

        if serializer.is_valid():
            responeseSerializer = serializer.save()

            profile_image = User.objects.filter(id=request.user.id).values()[
                0]['profile_image']

            data = upload_image_imagekit(profile_image)

            User.objects.filter(id=request.user.id).update(
                profile_image="", url_picture=data['url'])
            # Delete one file using path

            return Response({
                "status": "success",
                "message": "Profile updated successfully",
                "url": data['url']
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "status": "error",
                "message": serializer.error_messages
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):

        if request.auth == None:
            return Response({
                "status": "error",
                "message": "Authentication required or invalid token",
            }, status=status.HTTP_400_BAD_REQUEST)

        userId = request.user.id
        data = User.objects.filter(id=userId).values()[0]

        username = data['username']

        picture_url = data['url_picture']

        if picture_url == None or picture_url == "/":
            picture_url = 'https://eu.ui-avatars.com/api/?name=' + \
                username + '&format=svg&background=0D8ABC&color=fff'

        if data['profile_image'] != '':
            picture_url = settings.MEDIA_URL + data['profile_image']

        reponse = {
            "profile_image":  picture_url,
            "username": data['username'],
            "about": data['about'],
            'is_public': data['is_public'],
        }

        return Response(reponse, status=status.HTTP_200_OK)


class UserFollowingViewSet(generics.UpdateAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = FollowingSerializer
    queryset = followers_mantainers.objects.all()

    def put(self, request):

        if request.auth == None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        body = request.data

        message = "Error"

        if request.data['isFollower'] == True:

            # Verify if exist the following
            if followers_mantainers.objects.filter(user_id=request.data['following_user_id'], following_user_id=request.user.id).exists():
                message = "Already following"
                return Response({
                    "status": "error",
                    "message": message,
                    "followers_number": followers_mantainers.objects.filter(following_user_id=request.user.id).count(),
                }, status=status.HTTP_400_BAD_REQUEST)

            followers_mantainers.objects.create(
                user_id_id=request.data['following_user_id'], following_user_id_id=request.user.id)
            message = "Following association created successfully"
        elif request.data['isFollower'] == False:
            followers_mantainers.objects.filter(
                user_id=request.data['following_user_id'], following_user_id=request.user.id).delete()
            message = "Following disassociation created successfully"

        return Response({
            "status": "success",
            "message": message,
            "followers_number": followers_mantainers.objects.filter(following_user_id=request.user.id).count(),
        }, status=status.HTTP_200_OK)

        # user = User.objects.get(id=request.user.id)
