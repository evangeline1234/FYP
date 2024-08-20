from ura_api import ura_api
import pandas as pd
import requests
import psycopg2



def fetch_carpark_avail_lots_data():
    # Retrieve relevant data from URA API
    ura = ura_api.ura_api('b51dd357-a994-4736-a8d5-cdf175bd6da3')
    avail_lots = pd.DataFrame(ura.car_pack_available_lots())
    return avail_lots



