import pandas as pd
import account
import os
import utils as tool
import facebook_api as fp
import json
import mysql
import time


def get_loc_json(lon, lat):
    query = tool.compose({'latitude': lat, "longitude": lon, "type": "adradiussuggestion"})
    out = fp.url_get('https://graph.facebook.com/v2.11/search?{}'.format(query), False)
    json_out = json.loads(out)
    return {
        "latitude": str(lat),
        "longitude": str(lon),
        "radius": str(json_out['data'][0]['suggested_radius']),
        "distance_unit": json_out['data'][0]['distance_unit']
    }


def crawl_info():
    names = ["LONGITUDE", "LATITUDE"]
    json_array = []
    i = 1
    pro_dir = account.pro_home + "/geo-finder/data"
    for file in os.listdir(pro_dir):
        df = pd.read_csv(pro_dir + '/' + file, usecols=names)
        for i in range(0, len(df)):
            if i > 25000:
                out = get_loc_json(round(df.iloc[i]['LONGITUDE'], 8), round(df.iloc[i]['LATITUDE'], 8))
                time.sleep(0.2)
                json_array.append(out)
                if len(json_array) == 100:
                    mysql.insert_coordinate(json_array)
                    json_array = []
                    print("100 records commit!")
            else:
                i = i + 1
    if len(json_array) > 0:
        mysql.insert_coordinate(json_array)
        print("all records commit!")
