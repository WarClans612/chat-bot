# -*- coding: utf-8 -*-
import urllib.request
import json
from pymongo import MongoClient
from sensor_fetch import sensor_config

def grab_raw_data_from_url(url):
    with urllib.request.urlopen(url) as response:
        raw_data = json.loads(response.read().decode('utf-8'))
    return raw_data

def connect_to_database():
    db_url = sensor_config.host
    db_name = sensor_config.db_name
    client = MongoClient(db_url, 27017)
    db = client[db_name]
    return db

def save_data_into_db(data, collection_name):
    '''
    Collection Name:
        pm25_data
        rainfall_data
        uvi_data
        pm25_station_data
        uvi_station_data
    '''
    collection_need_renew = ['pm25_station_data', 'uvi_station_data']
    db = connect_to_database()
    if collection_name in collection_need_renew:
        db.drop_collection(collection_name)
    collect = db[collection_name]
    insert_status = collect.insert_many(data)
    if len(insert_status.inserted_ids) == len(data):
        return True
    else:
        return False

def save_weather_to_db(weather_data):
    save_status = True
    db = connect_to_database()
    collect = db['weather_data']
    for data in weather_data:
        upflag = collect.find_one_and_update({'endTime':data['endTime'],"locationName":data['locationName']}, { '$set' : { "temperature": data['temperature'], "rainfull_prob": data['rainfull_prob'], "Wx": data['Wx']}  }  )
        if upflag == None:
            insert_status = collect.insert_one(data)
            if insert_status == None:
                save_status = False
    return save_status
