from urllib import response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, ListAPIView, UpdateAPIView
from ..models import setting, feature_flag
from .serializers   import settingSerializers, featureFlagsSerializers
from .permissions import IsOwner
from rest_framework import filters, generics, permissions, status


from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
class SettingListAPIview(RetrieveUpdateAPIView):

    serializer_class = settingSerializers
    queryset = setting.objects.all()
    permissions_class = (permissions.IsAuthenticated,) 

    def get_queryset(self):

        if self.request.auth== None:

            return Response({
                "status": "error",
                "message": "Authentication required or invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)


        pk = self.kwargs['pk']

        return self.queryset.filter(owner_id=self.request.user.id, id=pk)


class FeatureFlagListAPIview(ListAPIView):

    serializer_class = featureFlagsSerializers
    queryset = feature_flag.objects.all()
    permissions_class = (permissions.IsAuthenticated,) 



class SettingListAPI_View(ListAPIView):

    queryset = setting.objects.all()
    serializer_class = settingSerializers
    permissions_class= (permissions.IsAuthenticated, IsOwner,) 
    

    filter_backends = [DjangoFilterBackend]
    my_filter_fields = ['is_active', 'is_switch_on']

    def get_kwargs_for_filtering(self):
        filtering_kwargs = {} 
        for field in  self.my_filter_fields: # iterate over the filter fields
            field_value = self.request.query_params.get(field) # get the value of a field from request query parameter
            if field_value: 
                
                # Check if string is boolean
                if field_value == 'true':
                    filtering_kwargs[field + '__in'] = [True]
                elif field_value == 'false':
                    filtering_kwargs[field + '__in'] = [False]
                else:
                    filtering_kwargs[field] = field_value

        return filtering_kwargs 

    def get_queryset(self):
        queryset = setting.objects.all() 
        filtering_kwargs = self.get_kwargs_for_filtering()
        
         # get the fields with values for filtering 
        if filtering_kwargs:
            queryset = setting.objects.filter(**filtering_kwargs) # filter the queryset based on 'filtering_kwargs'
        return queryset
