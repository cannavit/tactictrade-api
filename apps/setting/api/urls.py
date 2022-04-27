# APIs Configuration
from django.urls    import  path
from .              import views


urlpatterns = [
    path('<int:id>', views.SettingDetailAPIView.as_view(), name='setting_one'),
]