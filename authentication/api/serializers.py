from rest_framework import serializers
from authentication.models import *
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
import json

"""Serializer for User """


class UserSocialSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = ['username', 'first_name',
                  'last_name', 'email', 'auth_provider']


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    is_staff = serializers.BooleanField(default=False)
    is_verified = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=False)
    class Meta:

        model = User

        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'password',
            'auth_provider',
            'is_staff',
            'is_verified',
            'is_active',
        ]

    def validate(self, attrs):

        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric")

        return attrs

    def create(self, validated_data):

        # validated_data['url_picture'] = 'https://eu.ui-avatars.com/api/?name=' + \
        #     validated_data['username'] + \
        #     '&format=svg&background=0D8ABC&color=fff'

        validated_data['url_picture'] = 'https://eu.ui-avatars.com/api/?name=' + \
            validated_data['username'] + \
            '&background=0D8ABC&color=fff'            

        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):

        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class EmailVerificationSerializer(serializers.Serializer):

    token = serializers.CharField(max_length=755)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(max_length=255, required=True, min_length=3)
    password = serializers.CharField(
        max_length=100, required=True, min_length=8, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=0, read_only=True)
    tokens = serializers.CharField(
        max_length=255, min_length=20, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'username', 'tokens')

    def validate(self, attrs):

        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        # TODO add if user accout use the provider email
        #  https://www.youtube.com/watch?v=d7OxfJZOIhQ [20:00]

        if not user:
            raise AuthenticationFailed('Invalid credentials')
        if not user.is_active:
            raise AuthenticationFailed(
                "User is not active, contact your admintrator")
        if not user.is_verified:
            raise AuthenticationFailed("User is not verified")

        tokens = user.tokens
        print(tokens)
        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens,
        }


class ProfileSerializers(serializers.HyperlinkedModelSerializer):

    profile_image = serializers.ImageField(
        max_length=None, allow_empty_file=True, allow_null=True, required=False)

    class Meta:
        model = User

        fields = (
            'username',
            'about',
            'profile_image',
            'is_public',
            'url_picture'
        )


class FollowingSerializer(serializers.ModelSerializer):

    isFollower = serializers.BooleanField(read_only=False, default=True)
    following_user_id = serializers.IntegerField(read_only=False)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = followers_mantainers
        fields = ("isFollower", "user_id", "following_user_id")
