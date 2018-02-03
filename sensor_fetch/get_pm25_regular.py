import urllib.request
import json
from datetime import datetime
from pymongo import MongoClient
from sensor_config import *

def grab_data():
    url = 'http://opendata2.epa.gov.tw/AQI.json'
    with urllib.request.urlopen(url) as response:
        raw_data = json.loads(response.read().decode('utf-8'))
    return raw_data

def save_pm25():
    raw_data = grab_data()
    pm25_data = []
    for item in raw_data:
        data = dict()
        if item['PM2.5'] in ["ND",""]:
            data['PM25'] = 0
        else:
            data['PM25'] = int(item['PM2.5'])
        data['County'] = item['County']
        data['PublishTime'] = datetime.strptime(item['PublishTime'], "%Y-%m-%d %H:%M")
        data['SiteName'] = item['SiteName']
        pm25_data.append(data)
    
    db_url = "{host}:27017".format(host=mongo_host)
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client[ 'bot']
    collect = db['pm25_data']
    collect.insert(pm25_data)
    
if __name__ == "__main__":
    save_pm25()
