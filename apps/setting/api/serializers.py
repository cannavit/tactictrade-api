

""" Maquinas EAM serializers """
# Danjo Rest Framework
from rest_framework import serializers
# Modelos
from ..models    import setting, feature_flag

class settingSerializers(serializers.ModelSerializer):
    class Meta:

        model  = setting
        fields = '__all__'

class featureFlagsSerializers(serializers.ModelSerializer):
    class Meta:
        model  = feature_flag
        fields = '__all__'

