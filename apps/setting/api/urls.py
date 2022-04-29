# APIs Configuration
from django.urls    import  path
from apps.setting.api.views  import SettingListAPIview, SettingListAPI_View, FeatureFlagListAPIview


urlpatterns = [
    path('v1', SettingListAPI_View.as_view(), name='setting'),
    path('v1/<int:pk>', SettingListAPIview.as_view(), name='setting_one'),
    path('v1/feature-flag', FeatureFlagListAPIview.as_view(), name='feature_flag'),

]