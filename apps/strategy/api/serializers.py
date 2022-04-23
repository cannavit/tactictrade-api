from email.policy import default
from rest_framework import serializers
from apps.authentication.models import User, followers_mantainers
from apps.strategy.models import strategyNews, symbolStrategy
from apps.authentication.models import User
from django.conf import settings
from apps.trading.models import trading_config


class OwnerStrategySerializers(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            'profile_image',
            'url_picture',
            'username',
        )


class SettingsSerializersPost(serializers.ModelSerializer):

    class Meta:
        model = strategyNews

        fields = '__all__'


class SettingsSerializers(serializers.ModelSerializer):

    class Meta:
        model = strategyNews
        fields = '__all__'

    def to_representation(self, instance):

        response = super().to_representation(instance)

        response['owner'] = OwnerStrategySerializers(instance.owner).data

        owner_id = instance.owner.id

        request = self.context.get("request")

        user_id = request.user.id

        try:
            response['is_owner'] = owner_id == user_id
            periodTime = response['period']
            period = periodTime[0:1]
        except:
            period = 'd'

        timer = str(response['timer'])
        response['timeTrade'] = timer + period
        response['symbolName'] = instance.symbol.symbolName
        response['symbolUrl'] = instance.symbol.url


        response['owner']['followers'] = followers_mantainers.objects.filter(
            user_id=instance.owner.id).count()

        response['owner']['mantainer_id'] = user_id

        response['numbers_likes'] = instance.likes.all().count()
        response['numbers_favorite'] = instance.favorite.all().count()


        strategy_obj = strategyNews.objects.filter(id=instance.id)

        response['is_favorite'] = strategy_obj.filter(
            favorite__in=[user_id]).count() > 0

        response['is_follower']  =  strategy_obj.filter(
            follower__in=[user_id]).count() > 0    

        response['is_liked'] = strategy_obj.filter(
            likes__in=[user_id]).count() > 0       

        # response['is_favorite'] = is_favorite

        response['likes_number'] = strategy_obj.filter(
            likes__in=[user_id]).count()



        response['post_image'] = response['url_image']

        if response['owner']['url_picture'] == None:
            response['owner']['profile_image'] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Circle-icons-profile.svg/1200px-Circle-icons-profile.svg.png'
        else:
            response['owner']['profile_image'] = response['owner']['url_picture']

        return response


class CreateSettingSerializers(serializers.HyperlinkedModelSerializer):

    # post_image = serializers.ImageField(max_length=None,allow_empty_file=True,allow_null=True, required=False)
    # is_public = serializers.BooleanField(required=False)
    # is_active = serializers.BooleanField(required=False)

    # # #? User manual stadistic strategy
    # net_profit = serializers.FloatField(required=False)
    # percentage_profitable = serializers.FloatField(required=False)
    # max_drawdown = serializers.FloatField(required=False)
    # # profit_factor = serializers.FloatField(required=False)
    # symbol = serializers.CharField(required=False)

    class Meta:
        model = strategyNews
        # fields = '__all__'
        fields = [
            # 'owner',
            'strategyNews',
            # 'symbol',
            # 'is_public',
            # 'is_active',
            # 'net_profit',
            # 'percentage_profitable',
            # 'max_drawdown',
            # 'profit_factor',
            # 'period',
            # 'timer',
            # 'description',
            # 'post_image',
        ]


class PutSettingSerializers(serializers.HyperlinkedModelSerializer):

    strategyNews = serializers.CharField(max_length=100, required=False)

    is_public = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)

    # ? User manual stadistic strategy
    net_profit = serializers.FloatField(required=False)
    percentage_profitable = serializers.FloatField(required=False)
    max_drawdown = serializers.FloatField(required=False)
    profit_factor = serializers.FloatField(required=False)

    class Meta:
        model = strategyNews

        fields = [
            'pk',
            'strategyNews',
            'is_public',
            'is_active',
            'net_profit',
            'percentage_profitable',
            'max_drawdown',
            'profit_factor',
            'period',
            'timer',
            'description',
            'post_image',
        ]


class PutStrategySocialSerializers(serializers.ModelSerializer):

    likes = serializers.BooleanField(required=False)
    favorite = serializers.BooleanField(required=False)
    follower = serializers.BooleanField(required=False)

    class Meta:
        model = strategyNews

        fields = [
            'likes',
            'favorite',
            'follower'
        ]
