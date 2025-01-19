import requests
import json
import pandas as pd
from django.core.management.base import BaseCommand
from carpark.models import CarparkRates
from ura_api import ura_api

class Command(BaseCommand):
    help = 'Fetch carpark rates from URA API and populate the CarparkRates table'

    def handle(self, *args, **kwargs):
        # Retrieve data from URA API
        ura = ura_api.ura_api('b51dd357-a994-4736-a8d5-cdf175bd6da3')
        carpark_rates = pd.DataFrame(ura.car_pack_list_and_rates())
        
        # Fill any nan values with 0
        carpark_rates = carpark_rates.fillna("0")
        # Convert time columns to datetime
        carpark_rates['startTime'] = pd.to_datetime(carpark_rates['startTime'], format='%I.%M %p')
        carpark_rates['endTime'] = pd.to_datetime(carpark_rates['endTime'], format='%I.%M %p')
        # Only get the number and remove "min"
        carpark_rates['weekdayMin'] = carpark_rates['weekdayMin'].str.split().str[0].astype(float).astype(int)
        carpark_rates['satdayMin'] = carpark_rates['satdayMin'].str.split().str[0].astype(float).astype(int)
        carpark_rates['sunPHMin'] = carpark_rates['sunPHMin'].str.split().str[0].astype(float).astype(int)
        # Remove "$" and convert to float
        carpark_rates['weekdayRate'] = carpark_rates['weekdayRate'].str.replace('$', '').astype(float)
        carpark_rates['satdayRate'] = carpark_rates['satdayRate'].str.replace('$', '').astype(float)
        carpark_rates['sunPHRate'] = carpark_rates['sunPHRate'].str.replace('$', '').astype(float)
        # Convert geometries column to JSON strings
        carpark_rates['geometries'] = carpark_rates['geometries'].apply(json.dumps)

        # Insert carpark rates data
        for _, row in carpark_rates.iterrows():
            CarparkRates.objects.create(
                id=row.name + 1,
                carparkcode=row['ppCode'],
                carparkname=row['ppName'],
                vehcat=row['vehCat'],
                starttime=row['startTime'],
                endtime=row['endTime'],
                weekdayrate=row['weekdayRate'],
                weekdaymin=row['weekdayMin'],
                satdayrate=row['satdayRate'],
                satdaymin=row['satdayMin'],
                sunphrate=row['sunPHRate'],
                sunphmin=row['sunPHMin'],
                parkingsystem=row['parkingSystem'],
                parkcapacity=row['parkCapacity'],
                geometries=row['geometries']
            )

        self.stdout.write(self.style.SUCCESS('Successfully fetched and populated CarparkRates table'))