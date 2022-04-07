from authentication.api.serializers import RegisterSerializer
from broker.models import broker
from trading.models import trading_config
from authentication.models import User
from broker.utils.init_broker import InitData
from strategy.models import strategyNews
import random
import string

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))


def create_bot_by_new_strategy(strategy, symbol):

    # email generated automatic for djanog

    # email = 'bot_' + strategy.symbol.symbol + '_' + str(strategy.id) + '@gmail.com'\

    symbol = symbol.replace("-", "")
    symbol = symbol.lower().rstrip()

    try:
        time = strategy.timer
        period = str(strategy.period[0:1])
        strategyNewsName = strategy.strategyNews
        strategyId = strategy.id

    except:
        time = str(strategy['timer'])
        period = str(strategy['period'][0:1])
        strategyNewsName = strategy['strategyNews']
        strategyId = strategy['id']

    time_preriod = time + period

    random_value = random_char(4)

    username = strategyNewsName.lower(
    ).rstrip().replace(" ", "") + '_' + time_preriod + '_' +  random_value

    email = username + '@' + symbol + '.com'

    username='bot'+symbol+random_value
    # Convert string to lowercase

    serializerRegister = RegisterSerializer(data={
        'username': username,
        'password': 'Passw0rd!@123@222',
        'email': email,
        'first_name': username,
        'last_name': username,
        'auth_provider': 'email',
        'is_staff': False,
        'is_verified': True,
        'is_active': True,
        'is_bot': True,
        })

    if serializerRegister.is_valid(raise_exception=True):
        user_serializer = serializerRegister.save()
        broker = InitData.init_broker(user_serializer.id)
    else:
        print(serializerRegister.errors)


    strategyNews(id=strategyId).follower.add(user_serializer.id)
    # Create bot user for this strategy
    strategyNews.objects.filter(id=strategyId).update(email_bot=email)
    
    
    trading_config.objects.create(
        owner_id=user_serializer.id,
        strategyNews_id=strategyId,
        broker_id=broker.id,
        quantityUSDLong=1000,
        useLong=True,
        stopLossLong=None,
        takeProfitLong=10,
        consecutiveLossesLong=3,
        quantityUSDShort=1,
        useShort=False,
        stopLossShort=-5,
        takeProfitShort=10,
        consecutiveLossesShort=3,
        is_active=True,
        is_active_short=False,
        is_active_long=True,
        close_trade_long_and_deactivate=True,
        close_trade_short_and_deactivate=True
    )

