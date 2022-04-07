# Generated by Django 4.0.3 on 2022-04-02 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='symbol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbolName', models.CharField(max_length=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='avatars/')),
            ],
        ),
    ]
