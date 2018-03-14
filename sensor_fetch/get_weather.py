# encoding=utf-8
from pprint import pprint
import urllib.request
import urllib.parse
import json
import os
import datetime as DT
from datetime import datetime #datetime.datetime
import pymongo
from pymongo import MongoClient
import get_weather_regular

def get_weather(Location_name,time):
    db_url = "127.0.0.1:27017"
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client['bot']
    collect = db['weather_data']
    
    if time == "now":
        now_time = datetime.now()
        time_we_want = now_time
    else:
        now_time = datetime.now()
        now_day = datetime(now_time.year, now_time.month, now_time.day, 12, 0, 0, 0)
        next_day = now_day + DT.timedelta(days=1)
        time_we_want = next_day
    
    item = collect.find_one({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want},'locationName':Location_name})
    if item == None:
        get_weather_regular.grab_data()
        item = collect.find_one({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want},'locationName':Location_name})
    if item == None:
        item = {}
        item["temperature"] = 28
        item["rainfull_prob"] = 0
        print("[ERR] in get_weather:  can not get weather data ")
    return item
    
if __name__ == "__main__":
    Location_name = "新竹市"
    time = "now"
    item = get_weather(Location_name,time)
    print(item)
    

