# -*- coding: utf-8 -*-
import urllib.request
import json
from pymongo import MongoClient
import datetime as DT
from datetime import datetime
from sensor_fetch import sensor_config

def _connect_to_database():
    db_url = sensor_config.host
    db_name = sensor_config.db_name
    client = MongoClient(db_url, 27017)
    db = client[db_name]
    return db

class SensorParam:
    def __init__(self, location_name, name, item_name, fetch_func, save_func, time='now'):
        self.location_name = location_name
        self.collection_name = name
        self.item_name = item_name
        self.fetch_func = fetch_func
        self.save_func = save_func
        self.time = time
    
    def fetch(self):
        return self.fetch_func()
    
    def save(self, data):
        return self.save_func(data)

class SensorUtil:
    _sensor_db = _connect_to_database()
    
    def grab_raw_data_from_url(self, url):
        try:
            with urllib.request.urlopen(url, timeout = 10) as response:
                raw_data = json.loads(response.read().decode('utf-8'))
            return raw_data
        except:
            return None
    
    def save_data_into_db(self, data, collection_name):
        '''
        Collection Name:
            pm25_data
            rainfall_data
            uvi_data
            pm25_station_data
            uvi_station_data
        '''
        if data is None:
            return False
        db = self._sensor_db
        collection_need_renew = ['pm25_station_data', 'uvi_station_data']
        if collection_name in collection_need_renew:
            db.drop_collection(collection_name)
        collect = db[collection_name]
        insert_status = collect.insert_many(data)
        if len(insert_status.inserted_ids) == len(data):
            return True
        else:
            return False
    
    def save_weather_to_db(self, weather_data):
        save_status = True
        db = self._sensor_db
        collect = db['weather_data']
        for data in weather_data:
            upflag = collect.find_one_and_update({'endTime':data['endTime'],"locationName":data['locationName']}, { '$set' : { "temperature": data['temperature'], "rainfull_prob": data['rainfull_prob'], "Wx": data['Wx']}  }  )
            if upflag == None:
                insert_status = collect.insert_one(data)
                if insert_status == None:
                    save_status = False
        return save_status
    
    def get_data(self, sensor_param):
        '''
            collection_name -> item_name:
                pm25_data -> PM25
                uvi_data -> UVI
                rainfall_data -> rainfall1hr, rainfall3hr, rainfall6hr, rainfall12hr, rainfall24hr
                weather_data -> temperature, rainfull_prob
        '''
        collection_name = sensor_param.collection_name
        location_name = sensor_param.location_name
        item_name = sensor_param.item_name
        db = self._sensor_db
        collect = db[collection_name]
        
        now_time = datetime.now()
        now_hour = datetime(now_time.year, now_time.month, now_time.day, now_time.hour, 0, 0, 0)
        
        #Special parts for weather
        if collection_name == 'weather_data':
            #Fetch the data for now
            if sensor_param.time == 'now':
                time_wanted = now_time
            #Fetch the data for the 'time' in 'hours' in the future
            else:
                time_wanted = now_time + DT.timedelta(hours=sensor_param.time)    
            item = collect.find_one({'endTime': {'$gt': time_wanted},'startTime': {'$lt': time_wanted},'locationName':location_name})
            #If required data not found in the DB, re fetch the data from source
            if item is None:
                sensor_param.save(sensor_param.fetch())
                item = collect.find_one({'endTime': {'$gt': time_wanted},'startTime': {'$lt': time_wanted},'locationName':location_name})
            return item
        
        #Initial data get from DB
        item = collect.find_one({'$and': [{'PublishTime': {'$eq': now_hour}}, {'$or': [{'County': {'$eq': location_name}},{'SiteName': {'$eq': location_name}}]} ]})
    
        #If required data not found in DB, re fetch the data from source
        if item is None or item[item_name] == 'ND':
            fetch_data = sensor_param.fetch()
            sensor_param.save(fetch_data)
            if fetch_data is not None:
                time = fetch_data[0]['PublishTime']
                item = collect.find_one({'$and': [{'PublishTime': {'$eq': time}}, {'$or': [{'County': {'$eq': location_name}},{'SiteName': {'$eq': location_name}}]} ]})
        #Change the time to the last hour and re search DB
        if item is None or item[item_name] == 'ND':
            before_hour = now_hour - DT.timedelta(hours=1)
            item = collect.find_one({'$and': [{'PublishTime': {'$gt': before_hour}}, {'$or': [{'County': {'$eq': location_name}},{'SiteName': {'$eq': location_name}}]} ]})
        #Change the time to the last day and re search DB
        if item is None or item[item_name] == 'ND':
            now_day = datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0, 0)
            item = collect.find_one({'$and': [{'PublishTime': {'$gt': now_day}}, {'$or': [{'County': {'$eq': location_name}},{'SiteName': {'$eq': location_name}}]} ]})
        
        if item is None or item[item_name] == 'ND':
            return None
        else:
            return item[item_name]
