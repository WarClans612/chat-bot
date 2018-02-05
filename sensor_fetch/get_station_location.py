import urllib.request
import json
from datetime import datetime
from pymongo import MongoClient
from sensor_config import *

def grab_pm25_station():
    url = 'http://opendata.epa.gov.tw/ws/Data/AQXSite/?$format=json'
    with urllib.request.urlopen(url) as response:
        raw_data = json.loads(response.read().decode('utf-8'))
    return raw_data
    
def grab_uvi_station():
    url = 'http://opendata.epa.gov.tw/ws/Data/UV/?$format=json'
    with urllib.request.urlopen(url) as response:
        raw_data = json.loads(response.read().decode('utf-8'))
    return raw_data

def get_pm25_station_location():
    raw_data = grab_pm25_station()
    pm25_station_data = []
    for i in raw_data:
        data = {}
        data['Lon'] = float(i['TWD97Lon'])
        data['Lat'] = float(i['TWD97Lat'])
        data['SiteName'] = i['SiteName']
        pm25_station_data.append(data)
    
    db_url = "{host}:27017".format(host=mongo_host)
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client[ 'bot']
    db.drop_collection('pm25_station_data')
    collect = db['pm25_station_data']
    collect.insert(pm25_station_data)
    
def get_uvi_station_location():
    raw_data = grab_uvi_station()
    uvi_station_data = []
    for i in raw_data:
        data = {}
        Lon = i['WGS84Lon'].split(',')
        Lat = i['WGS84Lat'].split(',')
        data['Lon'] = float(Lon[0]) + float(Lon[1])/100 + float(Lon[2])/10000
        data['Lat'] = float(Lat[0]) + float(Lat[1])/100 + float(Lat[2])/10000
        data['SiteName'] = i['SiteName']
        uvi_station_data.append(data)
    
    db_url = "{host}:27017".format(host=mongo_host)
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client[ 'bot']
    db.drop_collection('uvi_station_data')
    collect = db['uvi_station_data']
    collect.insert(uvi_station_data)

if __name__ == "__main__":
    get_pm25_station_location()
    get_uvi_station_location()
