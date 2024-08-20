from django.urls import path
from .views import CarparkRatesAPI, NearbyCarparkAPI

urlpatterns = [
    path('carpark-rates/', CarparkRatesAPI.as_view(), name='carpark-rates'),
    path('nearby-carparks/', NearbyCarparkAPI.as_view(), name='nearby_carparks'),
]