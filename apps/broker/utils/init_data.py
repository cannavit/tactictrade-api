from apps.broker.api.serializers import brokerSerializers as serializer
from apps.setting.api.serializers import settingSerializers as setting_serializer
class InitData:

    def init_broker(userId):

        data = {
            'owner': userId,
            'is_paper_trading': True,
            'capital': 100000,
            'broker': 'paperTrade',
            'brokerName': 'Zipi Paper Trade',
            'second_broker_name': 'Bot',
            'tagBroker': 'new',
            'tagPrice': 'Paper Trading',
            'is_active': True,
            'block_is_active': True,
            
        }

        serializerData = serializer(data=data)

        if serializerData.is_valid(raise_exception=True):
            data = serializerData.save()
            return data
        else:
            return ""

    def init_settings(userId):
        
        # notifications_push_short

        data = {
            'owner':  userId,
            'setting': 'notifications_push_short',
            'is_active': True,
            'bool_value': True,
            'string_value': '',
            'is_switch_on': True,
            'icon': '0xf234',
            'family': 'notifications',
        }

        serializer_data = setting_serializer(data=data)

        if serializer_data.is_valid(raise_exception=True):    
            serializer_data.save()

        # notifications_push_long
        data = {
            'owner':  userId,
            'setting': 'notifications_push_long',
            'is_active': True,
            'bool_value': True,
            'string_value': '',
            'is_switch_on': True,
            'icon': '0xf234',
            'family': 'notifications',

        }

        serializer_data = setting_serializer(data=data)

        if serializer_data.is_valid(raise_exception=True):    
            serializer_data.save()        
        
        # en
        data = {
            'owner':  userId,
            'setting': 'language',
            'is_active': True,
            'bool_value': False,
            'string_value': 'en',
            'is_switch_on': False,
        }

        serializer_data = setting_serializer(data=data)

        if serializer_data.is_valid(raise_exception=True):    
            serializer_data.save()     

