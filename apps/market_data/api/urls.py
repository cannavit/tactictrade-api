from django.urls import path
from django.urls.resolvers import URLPattern
from django.conf.urls.static import static
from django.conf import settings
from .views import YahooFinView

# PERIOD:
# Range of time for read 
# INTERVAL: row size of data

# Example: 
# Get one month of data with interval of 30min
# /AAPL/1mo/30m

urlpatterns = [
    path('yahoo/<slug:symbolName>/<slug:period>/<slug:interval>/<slug:strategy>', YahooFinView.as_view(), name='yahoo_data'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
