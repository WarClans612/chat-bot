# -*- coding: utf-8 -*-
import os
from datetime import datetime
import pymongo
from pymongo import MongoClient
from sensor_fetch import util

def sensor_highest_value(handle_code,HL):
    table_mapping = {"PM25": "pm25_data","temperature": "weather_data", "UVI": "uvi_data", "RAINFALL": "rainfall_data"}
    db = util.connect_to_database()
    collect = db[table_mapping[handle_code]]
    
    #Initializing return dict
    values = {}
    handle_code_list = {'PM25': 'PM25', 'UVI': 'UVI', 'RAINFALL': 'rainfall24hr'}
    for key, data in handle_code_list.items():
        values[data] = 0
    values['temperature'] = 0
    
    #Preparing sort code
    if HL == "L":
        sort_code = 1
    else: #HL == "H"
        sort_code = -1

    #Sort value for each data type to get max
    if handle_code in handle_code_list:
        keys = handle_code_list[handle_code]
        data_list = collect.find().sort([("PublishTime",-1),(keys, sort_code)])
        if data_list is None:
            return None
        space = data_list[0]["County"]
        values[keys] = data_list[0][keys]
    else: #temperature
        now_time = datetime.now()
        data_list = collect.find({'endTime': {'$gt': now_time},'startTime': {'$lt': now_time}}).sort([("PublishTime",-1),("temperature",sort_code)])
        if data_list is None:
            return None
        space = data_list[0]["locationName"]
        values["temperature"] = data_list[0]["temperature"]
    
    return values, space