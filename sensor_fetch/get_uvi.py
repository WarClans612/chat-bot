import urllib.request
import json
import os
import datetime as DT
from datetime import datetime
import pymongo
from pymongo import MongoClient
import get_uvi_regular

Taiwan_county = [
"臺北市",
"新北市",
"桃園市",
"臺中市",
"臺南市",
"高雄市",
"基隆市",
"新竹市",
"嘉義市",
"新竹縣",
"苗栗縣",
"彰化縣",
"南投縣",
"雲林縣",
"嘉義縣",
"屏東縣",
"宜蘭縣",
"花蓮縣",
"臺東縣",
"澎湖縣"
]


def get_uvi(Location_name):
    if Location_name == "新竹市":
        Location_name = "新竹縣"
        
    db_url = "127.0.0.1:27017"
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client['bot']
    collect = db['uvi_data']
    
    now_time = datetime.now()
    now_hour = datetime(now_time.year, now_time.month, now_time.day, now_time.hour, 0, 0, 0)
    item = collect.find_one({'PublishTime': {'$eq': now_hour},'County':Location_name})
    
    if item == None:
        before_hour = now_hour - DT.timedelta(hours=1)
        item = collect.find_one({'PublishTime': {'$eq': before_hour},'County':Location_name})
        if item == None:
            before_hour = before_hour - DT.timedelta(hours=1)
            item = collect.find_one({'PublishTime': {'$eq': before_hour},'County':Location_name})
            if item == None:
                now_day = datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0, 0)
                item = collect.find_one({'PublishTime': {'$gt': now_day},'County':Location_name})
                if item == None:
                    return 0.0
        uvi = item['UVI']
    else:
        uvi = item['UVI']
    
    return uvi
    
def get_uvi_station(SiteName):      
    db_url = "127.0.0.1:27017"
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client['bot']
    collect = db['uvi_data']
    
    now_time = datetime.now()
    now_hour = datetime(now_time.year, now_time.month, now_time.day, now_time.hour, 0, 0, 0)
    item = collect.find_one({'PublishTime': {'$eq': now_hour},'SiteName':SiteName})
    
    if item == None:
        before_hour = now_hour - DT.timedelta(hours=1)
        item = collect.find_one({'PublishTime': {'$eq': before_hour},'SiteName':SiteName})
        if item == None:
            before_hour = before_hour - DT.timedelta(hours=1)
            item = collect.find_one({'PublishTime': {'$eq': before_hour},'SiteName':SiteName})
            if item == None:
                now_day = datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0, 0)
                item = collect.find_one({'PublishTime': {'$gt': now_day},'SiteName':SiteName})
                if item == None:
                    return 0.0
        uvi = item['UVI']
    else:
        uvi = item['UVI']
    
    return uvi
    
def get_county():
    db_url = "127.0.0.1:27017"
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client['bot']
    collect = db['uvi_data']
    
    now_time = datetime.now()
    now_hour = datetime(now_time.year, now_time.month, now_time.day, now_time.hour, 0, 0, 0)
    before_hour = now_hour  - DT.timedelta(hours=1)
    data_list = collect.find({'PublishTime': {'$eq': before_hour}})
    
    county_list = Taiwan_county.copy()
    
    for data in data_list:
        if data["County"] in county_list:
            county_list.remove(data["County"])
    print(county_list)
    
    
if __name__ == "__main__":
    uvi = get_uvi("新竹市")
    print(uvi)
    
    #get_county()
