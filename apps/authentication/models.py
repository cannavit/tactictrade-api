from django.db import models
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import datetime

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have an username")

        user = self.model(username=username,
                          email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None):

        if password is None:
            raise TypeError("Superusers must have a password")
        """Creates and saves a new super user"""

        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    AUTH_PROVIDERS = {
        'facebook': 'facebook',
        'google': 'google',
        'twitter': 'twitter',
        'email': 'email',
    }

    username = models.CharField(
        max_length=255, unique=False, db_index=True, null=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    is_bot = models.BooleanField(default=False)

    # http://localhost:8000/profile_image/unnamed.png
    profile_image = models.ImageField(
        upload_to='profile_image', blank=True, null=True)
    url_picture = models.URLField(blank=True, null=True, default='')

    about = models.TextField(blank=True, null=True, max_length=400, default="")

    auth_provider = models.CharField(
        max_length=255, choices=AUTH_PROVIDERS.items(),
        default=AUTH_PROVIDERS.get('email')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):

        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class followers_mantainers(models.Model):

    user_id = models.ForeignKey(
        to=User, related_name="mantainer", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(
        to=User, related_name="followers_users", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'following_user_id'],  name="unique_followers")
        ]

        ordering = ["-created"]

    def __str__(self):
        return self.user_id.username
