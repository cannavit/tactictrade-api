# Generated by Django 4.0.4 on 2022-04-27 18:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='symbolStrategy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbolName', models.CharField(max_length=10, unique=True)),
                ('symbolName_corrected', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='symbol/')),
                ('url', models.URLField(blank=True, null=True)),
                ('is_crypto', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='strategyNews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategyNews', models.CharField(max_length=60)),
                ('pusher', models.CharField(blank=True, choices=[('https://s3.tradingview.com/userpics/6171439-Hlns_big.png', 'TradingView')], default='tradingview', max_length=60, null=True)),
                ('is_public', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('net_profit', models.FloatField(default=0)),
                ('percentage_profitable', models.FloatField(default=0)),
                ('max_drawdown', models.FloatField(default=0)),
                ('profit_factor', models.FloatField(default=0)),
                ('is_verified', models.BooleanField(default=False)),
                ('net_profit_verified', models.FloatField(blank=True, default=0, null=True)),
                ('percentage_profitable_verified', models.FloatField(blank=True, default=0, null=True)),
                ('ranking', models.IntegerField(blank=True, default=0, null=True)),
                ('strategy_link', models.CharField(blank=True, default='', max_length=400, null=True)),
                ('strategy_token', models.CharField(blank=True, max_length=400, null=True, unique=True)),
                ('period', models.CharField(blank=True, choices=[('minutes', 'm'), ('hours', 'h'), ('days', 'd'), ('weeks', 'w')], default='hours', max_length=60, null=True)),
                ('timer', models.IntegerField(blank=True, default=1, null=True)),
                ('description', models.TextField(blank=True, max_length=600, null=True)),
                ('post_image', models.ImageField(blank=True, upload_to='strategy_post_image')),
                ('url_image', models.URLField(blank=True, default='', null=True)),
                ('email_bot', models.CharField(blank=True, default='', max_length=60, null=True)),
                ('favorite', models.ManyToManyField(blank=True, related_name='favorite', to=settings.AUTH_USER_MODEL)),
                ('follower', models.ManyToManyField(blank=True, related_name='follower', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maintainer', to=settings.AUTH_USER_MODEL)),
                ('symbol', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='strategy.symbolstrategy')),
            ],
        ),
    ]
