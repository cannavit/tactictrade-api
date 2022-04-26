# Generated by Django 4.0.4 on 2022-04-25 11:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_cryptography.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='broker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capital', models.FloatField(default=0)),
                ('isPaperTrading', models.BooleanField(default=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('broker', models.CharField(choices=[('alpaca', 'Alpaca'), ('paperTrade', 'paperTrade')], default='paperTrade', max_length=255)),
                ('tagBroker', models.CharField(blank=True, default='', max_length=20)),
                ('tagPrice', models.CharField(blank=True, default='', max_length=20)),
                ('isActive', models.BooleanField(default=True)),
                ('block_is_active', models.BooleanField(default=False)),
                ('brokerName', models.CharField(default='Zipi Paper Trade', max_length=255)),
                ('urlLogo', models.CharField(default='', max_length=255)),
                ('short_is_allowed', models.BooleanField(default=True)),
                ('short_allowed_fractional', models.BooleanField(default=True)),
                ('long_is_allowed', models.BooleanField(default=True)),
                ('long_allowed_fractional', models.BooleanField(default=True)),
                ('short_is_allowed_crypto', models.BooleanField(default=True)),
                ('short_allowed_fractional_crypto', models.BooleanField(default=True)),
                ('long_is_allowed_crypto', models.BooleanField(default=True)),
                ('long_allowed_fractional_crypto', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='alpaca_configuration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('APIKeyID', models.CharField(max_length=255)),
                ('SecretKey', django_cryptography.fields.encrypt(models.CharField(max_length=50))),
                ('endpoint', models.CharField(choices=[('https://paper-api.alpaca.markets', 'https://paper-api.alpaca.markets'), ('Add URL by Production URL', 'Add URL by Production URL')], default='https://paper-api.alpaca.markets', max_length=255)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='broker.broker')),
            ],
        ),
    ]
