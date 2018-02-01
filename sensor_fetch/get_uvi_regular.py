import urllib.request
import json
from datetime import datetime
from pymongo import MongoClient
from sensor_config import *

def grab_data():
    url = 'http://opendata.epa.gov.tw/ws/Data/UV/?$format=json'
    with urllib.request.urlopen(url) as response:
        data_list = json.loads(response.read().decode('utf-8'))
    
    return data_list

def save_uvi():
    data_list = grab_data()
    print(data_list)
    new_data_list = []
    for i in data_list:
        time = datetime.strptime(i['PublishTime'], "%Y-%m-%d %H:%M")
        data = {}
        data['County'] = i['County']
        if i['UVI'] == "":
            data['UVI'] = 0.0
        elif float(i['UVI']) > 0:
            data['UVI'] = float(i['UVI'])
        else:
            data['UVI'] = 0.0
        data['PublishTime'] = time
        data['SiteName'] = i['SiteName']
        data['WGS84Lon'] = i['WGS84Lon']
        data['WGS84Lat'] = i['WGS84Lat']
        new_data_list.append(data)
    
    db_url = "{host}:27017".format(host=mongo_host)
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client[ 'bot']
    collect = db['uvi_data']
    collect.insert(new_data_list)
    
    return time
    
if __name__ == "__main__":
    save_uvi()
