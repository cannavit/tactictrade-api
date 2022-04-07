from django.urls import path
from django.urls.resolvers import URLPattern
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', RegisterViewSet.as_view(), name='register_new_user'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('email-verify/', VerifyEmail.as_view(), name='email-verify'),
    path('profile/', ProfileListAPIview.as_view(), name='profile'),
    path('following/', UserFollowingViewSet.as_view(), name='following')
    # path('followers/', UserFollowingViewSet.as_view({'get': 'list'}), name='followers'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
