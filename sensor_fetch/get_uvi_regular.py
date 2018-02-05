import urllib.request
import json
from datetime import datetime
from pymongo import MongoClient
from sensor_config import *

def grab_data():
    url = 'http://opendata.epa.gov.tw/ws/Data/UV/?$format=json'
    with urllib.request.urlopen(url) as response:
        raw_data = json.loads(response.read().decode('utf-8'))
    return raw_data

def save_uvi():
    raw_data = grab_data()
    uvi_data = []
    for item in raw_data:
        data = {}
        if item['UVI'] == "":
            data['UVI'] = 0.0
        elif float(item['UVI']) > 0:
            data['UVI'] = float(item['UVI'])
        else:
            data['UVI'] = 0.0
        data['County'] = item['County']
        data['PublishTime'] = datetime.strptime(item['PublishTime'], "%Y-%m-%d %H:%M")
        data['SiteName'] = item['SiteName']
        data['WGS84Lon'] = item['WGS84Lon']
        data['WGS84Lat'] = item['WGS84Lat']
        uvi_data.append(data)
    
    db_url = "{host}:27017".format(host=mongo_host)
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client[ 'bot']
    collect = db['uvi_data']
    collect.insert(uvi_data)
    
if __name__ == "__main__":
    save_uvi()
