

""" Maquinas EAM serializers """
# Danjo Rest Framework
from rest_framework import serializers
# Modelos
from ..models    import setting, feature_flag

class settingSerializers(serializers.ModelSerializer):
    class Meta:

        model  = setting
        fields = '__all__'

        # fields = [
        #     'owner',
        #     'setting',
        #     'family',
        #     'is_active',
        #     'bool_value',
        #     'string_value',
        #     'icon',
        #     'is_switch_on',
        # ]

class featureFlagsSerializers(serializers.ModelSerializer):
    class Meta:
        model  = feature_flag
        fields = '__all__'

