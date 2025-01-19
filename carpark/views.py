from django.shortcuts import render
from rest_framework import viewsets
from .models import CarparkRates
from .serializers import CarparkRatesSerializer, NearbyCarparkSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from math import radians, cos, sin, asin, sqrt
from pyproj import Proj, Transformer, transform
from geopy.distance import geodesic
from .utils.get_carpark_avail_lots_data import fetch_carpark_avail_lots_data
import pandas as pd


# Create your views here.

# This view is to get carpark rates data of specific vehicle category
class CarparkRatesAPI(APIView):
    permission_classes = [permissions.AllowAny]

    """
    # This function is to get all carpark rates data (use this if Yu Ze wants all carpark rates data for his visualization)
    def post(self, request, *args, **kwargs):
        # Get all unique carpark codes
        carpark_codes = CarparkRates.objects.values_list('carparkcode', flat=True).distinct()

        # Organize the format of the rates data to be returned
        organized_data = {}
        for carparkcode in carpark_codes:
            carpark_rates = CarparkRates.objects.filter(carparkcode=carparkcode)
            if carpark_rates.exists():
                carparkname = carpark_rates.first().carparkname
                rates_data = {}
                for rate in carpark_rates:
                    vehcat = rate.vehcat
                    if vehcat not in rates_data:
                        rates_data[vehcat] = CarparkRatesSerializer(rate).data
                organized_data[carparkcode] = {
                    'carparkname': carparkname,
                    'rates': rates_data
                }

        if organized_data:
            return Response(organized_data, status=status.HTTP_200_OK)
        else:
            return Response("No carpark rates found", status=status.HTTP_404_NOT_FOUND) 
    """

    # This function is to get carpark rates data for a specified carpark code
    def post(self, request, *args, **kwargs):
        carparkcode = request.data.get('carparkcode')
        
        # Get carpark rates data of specific carpark code
        carpark_rates = CarparkRates.objects.filter(carparkcode=carparkcode)

        # Organize the format of the rates data to be returned
        organized_data = {}
        for rate in carpark_rates:
            vehcat = rate.vehcat
            if vehcat not in organized_data:
                organized_data[vehcat] = CarparkRatesSerializer(rate).data
            
        if organized_data:
            response_data = {
                'carparkcode': carparkcode,
                'carparkname': carpark_rates.first().carparkname if carpark_rates.exists() else None,
                'rates': organized_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response("No carpark rates found", status=status.HTTP_404_NOT_FOUND)
        

class NearbyCarparkAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user_lat = request.data.get('latitude')
        user_lon = request.data.get('longitude')
        
        if not user_lat or not user_lon:
            return Response({"error": "Latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except ValueError:
            return Response({"error": "Latitude and longitude must be valid float numbers"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call fetch_carpark_avail_lots_data function to get carpark rates data
        try:
            avail_lots = fetch_carpark_avail_lots_data()
            avail_lots = pd.DataFrame(avail_lots) 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = NearbyCarparkSerializer(data={
            'user_lat': user_lat,
            'user_lon': user_lon,
            'avail_lots': avail_lots.to_dict(orient='records')
        })

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
        nearby_carparks = []

    

        for carpark in:
            # Get coordinates of the carpark
            geometries = carpark.geometries
            
            coordinates_str = geometries[0]['coordinates']
            lat, lon = map(float, coordinates_str.split(','))

            # Convert lat and lon from SVY21 to EPSG:3785
            lon, lat = convert_svy21_to_epsg3785(lat, lon)
            user_location = (user_lat, user_lon)
            carpark_location = (lat, lon)
            distance = geodesic(user_location, carpark_location).kilometers
            print("Distance: ", distance)
            if distance <= 10: # Distance less than or equal to 10km
                nearby_carparks.append({
                    "carparkcode": carpark.carparkNo,
                    "lot_type": carpark.lotType,
                    "lots_available": carpark.lotsAvailable,
                    "distance": distance,
                    "Latitude": lat,
                    "Longitude": lon
                })
    

        # Organize the response data in a structured format
        if nearby_carparks:
            response_data = {
                "nearby_carparks": nearby_carparks
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response("No nearby carparks found within the specified distance", status=status.HTTP_404_NOT_FOUND)
"""