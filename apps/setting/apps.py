from django.apps import AppConfig



class SettingConfig(AppConfig):
    # optional, add default auto field
    default_auto_field = 'django.db.models.BigAutoField'
    # set location of app using sub dir
    name = 'apps.setting'
    # optional, add name of app
    # verbose_name = 'My App Verbose Name'
