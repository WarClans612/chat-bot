import urllib.request
import json
import os
import datetime as DT
from datetime import datetime
import pymongo
from pymongo import MongoClient
from sensor_fetch.util import SensorUtil

rainbow_list = ["晴午後短暫陣雨","晴午後短暫雷陣雨"]
sunlist = ["晴午後短暫陣雨","晴午後短暫雷陣雨","晴天","晴時多雲"]
recommend_mapping = {"臺東縣": "太麻里"}

def search_time_for_rainbow(slots):
    now_time = datetime.now()
    time = slots["time"]
    if time == "now":
        return now_time
    else:
        now_day = datetime(now_time.year, now_time.month, now_time.day, 12, 0, 0, 0)
        next_day = now_day + DT.timedelta(days=1)
        return next_day
        
def search_time_for_sunrise():
    now_time = datetime.now()
    if now_time.hour < 6:
        return datetime(now_time.year, now_time.month, now_time.day, 6, 1, 0, 0)
    else:
        next_day = now_time + DT.timedelta(days=1)
        return datetime(next_day.year, next_day.month, next_day.day, 6, 1, 0, 0)

def location_of_sky_condition(types, slots = None):
    '''
        types --> rainbow, sunrise
        if types == sunrise, then slots don't have to be given as argument
    '''
    client = SensorUtil()
    db = client._sensor_db
    collect = db["weather_data"]
    
    wanted_list = None
    if types == "rainbow":
        wanted_list = rainbow_list
        time_we_want = search_time_for_rainbow(slots)
    elif types == "sunrise":
        wanted_list = sunlist
        time_we_want = search_time_for_sunrise()
    else:
        return None
    
    data_list = []
    for messages in wanted_list:
        data_list.append(collect.find({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want}, 'Wx': messages}))

    county_list = []
    for data in data_list:
        for county in data:
            county_list.append(county['locationName'])

    if types == "rainbow":
        return county_list
    elif types == "sunrise":
        recommend_list = []
        for data in county_list:
            if data in recommend_mapping:
                recommend_list.append( recommend_mapping[data] )
        return recommend_list, county_list

def on_sky(types, slots):
    '''
        types --> rainbow, sunrise
        if types == sunrise, then slots don't have to be given as argument
    '''
    client = SensorUtil()
    db = client._sensor_db
    collect = db["weather_data"]
    
    Location_name = slots["space"]
    
    wanted_list = None
    if types == "rainbow":
        wanted_list = rainbow_list
        time_we_want = search_time_for_rainbow(slots)
    elif types == "sunrise":
        wanted_list = sunlist
        time_we_want = search_time_for_sunrise()
    else:
        return False, None
        
    item = collect.find_one({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want},'locationName':Location_name})
    if item is None:
        return None
    wx = item["Wx"]
    
    if wx in wanted_list:
        result = True
    else:
        result = False
    
    return result, wx
