from rest_framework import serializers
from . import google
from django.conf import settings
from .register import register_social_user


class GoogleSocialAuthSerializer(serializers.Serializer):

    auth_token = serializers.CharField(required=True)

    def validate_auth_token(self, auth_token):

        user_data = google.Google.validate(auth_token)

        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                user_data
            )

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'

        return register_social_user(
            provider=provider,
            user_id=user_id,
            email=email,
            name=name,
            picture=user_data['picture']
        )
