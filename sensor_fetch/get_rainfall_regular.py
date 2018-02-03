import urllib.request
import json
from datetime import datetime
from pymongo import MongoClient
from sensor_config import *

def grab_data():
    url = 'http://opendata.epa.gov.tw/ws/Data/RainTenMin/?format=json'
    with urllib.request.urlopen(url) as response:
        raw_data = json.loads(response.read().decode('utf-8'))
    return raw_data

def save_rainfall():
    raw_data = grab_data()
    rainfall_data = []
    for item in raw_data:
        data = dict()
        data['County'] = item['County']
        data['rainfall1hr'] = float(item['Rainfall1hr'])
        data['rainfall24hr'] = float(item['Rainfall24hr'])
        data['PublishTime'] = datetime.strptime(item['PublishTime'], "%Y-%m-%d %H:%M:%S")
        rainfall_data.append(data)
    
    db_url = "{host}:27017".format(host=mongo_host)
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client[ 'bot']
    collect = db['rainfall_data']
    collect.insert(rainfall_data)
    
if __name__ == "__main__":
    save_rainfall()
