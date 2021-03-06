# Generated by Django 4.0.4 on 2022-04-27 18:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('strategy', '0001_initial'),
        ('broker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='strategy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy', models.CharField(max_length=255)),
                ('order', models.CharField(blank=True, max_length=255, null=True)),
                ('contracts', models.CharField(blank=True, max_length=255, null=True)),
                ('ticker', models.CharField(blank=True, max_length=255, null=True)),
                ('position_size', models.CharField(blank=True, max_length=255, null=True)),
                ('bot_token', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='trading_config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantityUSDLong', models.FloatField(blank=True, default=0, null=True)),
                ('quantityQTYLong', models.FloatField(blank=True, default=0, null=True)),
                ('useLong', models.BooleanField(blank=True, default=False, null=True)),
                ('stopLossLong', models.FloatField(blank=True, default=-3, null=True)),
                ('takeProfitLong', models.FloatField(blank=True, default=10, null=True)),
                ('consecutiveLossesLong', models.IntegerField(blank=True, default=3, null=True)),
                ('quantityUSDShort', models.FloatField(blank=True, default=0, null=True)),
                ('quantityQTYShort', models.FloatField(blank=True, default=0, null=True)),
                ('useShort', models.BooleanField(blank=True, default=False, null=True)),
                ('stopLossShort', models.FloatField(blank=True, default=-3, null=True)),
                ('takeProfitShort', models.FloatField(blank=True, default=10, null=True)),
                ('consecutiveLossesShort', models.IntegerField(blank=True, default=3, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('initialCapitalUSDLong', models.FloatField(blank=True, default=0, null=True)),
                ('initialCapitalUSDShort', models.FloatField(blank=True, default=0, null=True)),
                ('initialCapitalQTYLong', models.FloatField(blank=True, default=0, null=True)),
                ('initialCapitalQTYShort', models.FloatField(blank=True, default=0, null=True)),
                ('initialQuantityLong', models.FloatField(blank=True, default=0, null=True)),
                ('initialQuantityShort', models.FloatField(blank=True, default=0, null=True)),
                ('winTradeLong', models.IntegerField(blank=True, default=0, null=True)),
                ('winTradeShort', models.IntegerField(blank=True, default=0, null=True)),
                ('closedTradeShort', models.IntegerField(blank=True, default=0, null=True)),
                ('closedTradeLong', models.IntegerField(blank=True, default=0, null=True)),
                ('profitPorcentageShort', models.FloatField(blank=True, default=0, null=True)),
                ('profitPorcentageLong', models.FloatField(blank=True, default=0, null=True)),
                ('is_active', models.BooleanField(blank=True, default=False, null=True)),
                ('is_active_short', models.BooleanField(blank=True, default=False, null=True)),
                ('is_active_long', models.BooleanField(blank=True, default=False, null=True)),
                ('close_trade_long_and_deactivate', models.BooleanField(blank=True, default=False, null=True)),
                ('close_trade_short_and_deactivate', models.BooleanField(blank=True, default=False, null=True)),
                ('is_paper_trading', models.BooleanField(blank=True, default=True, null=True)),
                ('numberOfTradesLong', models.IntegerField(blank=True, default=0, null=True)),
                ('numberOfWindTradeLong', models.IntegerField(blank=True, default=0, null=True)),
                ('currentLongUSDvalue', models.FloatField(blank=True, default=0, null=True)),
                ('percentageProfitLong', models.FloatField(blank=True, default=0, null=True)),
                ('numberOfTradesShort', models.IntegerField(blank=True, default=0, null=True)),
                ('numberOfWindTradeShort', models.IntegerField(blank=True, default=0, null=True)),
                ('currentShortUSDvalue', models.FloatField(blank=True, default=0, null=True)),
                ('percentageProfitShort', models.FloatField(blank=True, default=0, null=True)),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='broker.broker')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('strategyNews', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strategy.strategynews')),
            ],
        ),
    ]
