from rest_framework import viewsets, permissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from ..models import setting
from .serializers   import settingSerializers
from .permissions import IsOwner


class SettingListAPIview(ListCreateAPIView):
    serializer_class = settingSerializers
    queryset = setting.objects.all()
    permissions_class = (permissions.IsAuthenticated,) 

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class SettingDetailAPIView(RetrieveUpdateDestroyAPIView):

    queryset = setting.objects.all()
    serializer_class = settingSerializers
    permissions_class= (permissions.IsAuthenticated, IsOwner,) 
    lookup_field = "id"

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
