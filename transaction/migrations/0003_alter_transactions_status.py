# Generated by Django 4.0.3 on 2022-04-03 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0002_transactions_amount_close_transactions_amount_open_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='status',
            field=models.CharField(choices=[('opened', 'opened'), ('success', 'success'), ('close', 'close'), ('pending', 'pending'), ('error', 'error'), ('close_pending', 'close_pending'), ('accepted', 'accepted')], default='closed', max_length=255),
        ),
    ]
