from .models import *
from broker.api.serializers import brokerSerializers as serializer
from authentication.models import User

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
