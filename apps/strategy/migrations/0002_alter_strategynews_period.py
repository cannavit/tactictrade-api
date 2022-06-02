# Generated by Django 4.0.4 on 2022-05-28 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategynews',
            name='period',
            field=models.CharField(blank=True, choices=[('minute', 'm'), ('hour', 'h'), ('day', 'd'), ('week', 'w'), ('year', 'y')], default='hours', max_length=60, null=True),
        ),
    ]
