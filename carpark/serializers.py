from rest_framework import serializers
from .models import CarparkRates
from geopy.distance import geodesic
import pandas as pd
from pyproj import Proj, transform

# This serializer is to specify the fields and format of the data to be returned
class CarparkRatesSerializer(serializers.ModelSerializer):
    weekday = serializers.SerializerMethodField()
    sat = serializers.SerializerMethodField()
    sunph = serializers.SerializerMethodField()

    class Meta:
        model = CarparkRates
        fields = ['weekday', 'sat', 'sunph']

    def get_weekday(self, obj):
        return [
            {
                'starttime': rate.starttime.strftime('%I:%M %p') if rate.starttime else None,
                'endtime': rate.endtime.strftime('%I:%M %p') if rate.endtime else None,
                'rate': rate.weekdayrate,
                'min': rate.weekdaymin
            }
            for rate in CarparkRates.objects.filter(carparkcode=obj.carparkcode, vehcat=obj.vehcat)
        ]

    def get_sat(self, obj):
        return [
            {
                'starttime': rate.starttime.strftime('%I:%M %p') if rate.starttime else None,
                'endtime': rate.endtime.strftime('%I:%M %p') if rate.endtime else None,
                'rate': rate.satdayrate,
                'min': rate.satdaymin
            }
            for rate in CarparkRates.objects.filter(carparkcode=obj.carparkcode, vehcat=obj.vehcat)
        ]

    def get_sunph(self, obj):
        return [
            {
                'starttime': rate.starttime.strftime('%I:%M %p') if rate.starttime else None,
                'endtime': rate.endtime.strftime('%I:%M %p') if rate.endtime else None,
                'rate': rate.sunphrate,
                'min': rate.sunphmin
            }
            for rate in CarparkRates.objects.filter(carparkcode=obj.carparkcode, vehcat=obj.vehcat)
        ]

def convert_svy21_to_epsg4326(easting, northing):
    """Converts SVY21 coordinates to EPSG:4326."""
    svy21 = Proj(init='epsg:3414')  # SVY21
    wgs84 = Proj(init='epsg:4326')  # WGS84 (EPSG:4326)
    x, y = transform(svy21, wgs84, easting, northing)
    return x, y


class NearbyCarparkSerializer(serializers.Serializer):
    user_lat = serializers.FloatField()
    user_lon = serializers.FloatField()
    avail_lots = serializers.ListField()

    def to_representation(self, instance):
        user_lat = instance['user_lat']
        user_lon = instance['user_lon']
        avail_lots = pd.DataFrame(instance['avail_lots'])

        # Extract unique carparkNo and geometries
        unique_carparks = avail_lots.drop_duplicates(subset=['carparkNo']).reset_index(drop=True)
        # Extract coordinates string
        unique_carparks['coordinates_str'] = unique_carparks['geometries'].apply(lambda x: x[0]['coordinates'] if x else '')
        # Filter out rows with empty coordinates_str
        unique_carparks = unique_carparks[unique_carparks['coordinates_str'] != '']
        # Convert coordinates_str from SVY21 to EPSG:4326
        unique_carparks['coordinates_str'] = unique_carparks['coordinates_str'].apply(lambda x: convert_svy21_to_epsg4326(float(x.split(',')[0]), float(x.split(',')[1])) if x else '')
        # get lon and lat from coordinates_str
        unique_carparks['lon'] = unique_carparks['coordinates_str'].apply(lambda x: x[0] if x else None)
        unique_carparks['lat'] = unique_carparks['coordinates_str'].apply(lambda x: x[1] if x else None)
        unique_carparks['lon'] = unique_carparks['lon'].astype(float)
        unique_carparks['lat'] = unique_carparks['lat'].astype(float)
        # Calculate distance between user location and carpark location in column 'distance'
        unique_carparks['user_location'] = unique_carparks.apply(lambda x: (user_lat, user_lon), axis=1)
        unique_carparks['carpark_location'] = unique_carparks.apply(lambda x: (x['lat'], x['lon']), axis=1)
        unique_carparks['distance'] = unique_carparks.apply(lambda x: geodesic(x['user_location'], x['carpark_location']).kilometers, axis=1)
    
        # Filter out carpark locations within 2km
        nearby_carparks = unique_carparks[unique_carparks['distance'] <= 2]
        nearby_carparks = nearby_carparks[['carparkNo', 'lat', 'lon', 'distance']]


        # Get carpark rates based on carparkNo
        carpark_rates = CarparkRates.objects.filter(carparkcode__in=nearby_carparks['carparkNo'])

        # Create a dictionary to map carparkNo to carparkname
        carpark_rates_dict = {rate.carparkcode: rate.carparkname for rate in carpark_rates}

        # Add carparkName to nearby_carparks
        nearby_carparks['carparkName'] = nearby_carparks['carparkNo'].map(carpark_rates_dict)

        # Rearrange columns
        nearby_carparks = nearby_carparks[['carparkNo', 'carparkName', 'lat', 'lon', 'distance']]
    
        # Convert DataFrame to list of dictionaries
        nearby_carparks_list = nearby_carparks.to_dict(orient='records')

        return {"nearby_carparks": nearby_carparks_list}

        
        """
        for _, carpark in unique_carparks.iterrows():
            geometries = carpark['geometries']
            coordinates_str = geometries[0]['coordinates']
            
            easting, northing = map(float, coordinates_str.split(','))

            # Convert lat and lon from SVY21 to EPSG:3785
            lon, lat = convert_svy21_to_epsg3785(easting, northing)
            print(lon, lat)

            user_location = (user_lat, user_lon)
            carpark_location = (lat, lon)
            distance = geodesic(user_location, carpark_location).kilometers

            if distance <= 5:
                nearby_carparks.append({
                    "carparkNo": carpark['carparkNo'],
                    "lotType": carpark['lotType'],
                    "lotsAvailable": carpark['lotsAvailable'],
                    "distance": distance,
                    "Latitude": lat,
                    "Longitude": lon
                })
    """
        