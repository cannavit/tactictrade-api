from django.contrib             import admin
from apps.setting.models import setting, feature_flag
from django.conf import settings
from apps.setting.models import feature_flag as feature_flag_model
from django.contrib import messages

from utils.convert_json_to_objects import convertJsonToObject

admin.site.site_header = 'TacticTrade-Api'


@admin.action(description='Create/Update Feature Flags')
def create_update_feature_flag(modeladmin, request, queryset):


    FEATURE_FLAGS = settings.FEATURE_FLAGS

    DJANGO_ENV = settings.DJANGO_ENV


    for feature in FEATURE_FLAGS:   
        #! Use only when is paper trading. 
        #? Note not use when is real trading.
        ## Close Open transaction
        feature = convertJsonToObject(feature)


        data = {
            "feature": feature.feature, 
            "description": feature.description,
            "family": feature.family,
            "localization": feature.localization,
            "family_id": feature.family_id,
            "flag_open": feature.flag_open,
            "version": feature.version,
            "version_app": feature.version_app
        }

        
        if DJANGO_ENV == 'dev' or DJANGO_ENV == 'development':
            data['flag_open'] = feature.is_development
        if DJANGO_ENV == 'prod' or DJANGO_ENV == 'production':
            data['flag_open'] = feature.is_production
        if DJANGO_ENV == 'staging':
            data['flag_open'] = feature.is_staging
        
        try:
            feature_flag_model.objects.get(feature=feature.feature)
            messages.warning(request, 'Exist '+ feature.feature + ' Successfully')

        except Exception as e:
            
            feature_flag_model.objects.create(
                    **data
                )

            messages.success(request, 'Create '+ feature.feature + ' Successfully')


        print("@Note-01 ---- -582967494 -----")
            # print(instance)


      
class settingAdmin(admin.ModelAdmin):

    list_display = [
            'id',
            'owner',
            'setting',
            'family',
            'is_active',
            'bool_value',
            'string_value',
            'is_switch_on',
        ]

    pass


admin.site.register(setting,settingAdmin)


class feature_flag_admin(admin.ModelAdmin):

    list_display = [
            'id',
            'feature',
            'description',
            'family',
            'localization',
            'family_id',
            'flag_open',
            'version',
            'version_app',
        ]

    actions = [create_update_feature_flag, ]

admin.site.register(feature_flag,feature_flag_admin)


