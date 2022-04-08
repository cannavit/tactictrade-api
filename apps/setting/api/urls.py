# APIs Configuration
from django.urls    import  path
from .              import views


urlpatterns = [
    path('', views.SettingListAPIview.as_view(), name='settings'),
    path('<int:id>', views.SettingDetailAPIView.as_view(), name='settings'),
]