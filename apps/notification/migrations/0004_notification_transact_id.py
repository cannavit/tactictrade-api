# Generated by Django 4.0.4 on 2022-04-25 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_notification_isclosed'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='transact_id',
            field=models.IntegerField(default=0),
        ),
    ]
