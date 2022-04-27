

""" Maquinas EAM serializers """
# Danjo Rest Framework
from rest_framework import serializers
# Modelos
from ..models    import setting

class settingSerializers(serializers.ModelSerializer):
    class Meta:

        model  = setting
        fields = '__all__'

