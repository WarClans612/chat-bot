import urllib.request
import json
import os
from datetime import datetime
import pymongo
from pymongo import MongoClient
import get_pm25_regular
table_mapping = {"PM25": "pm25_data","temperature": "weather_data", "UVI": "uvi_data"}

def get_most(handle_code,HL):
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client['bot']
	collect = db[table_mapping[handle_code]]
	values = {}
	values["pm25"] = 0
	values["uvi"] = 0
	values["temperature"] = 0
	
	if HL == "H":
		sort_code = -1
	else :
		sort_code = 1
		
	if handle_code == "PM25":
		data_list = collect.find().sort([("PublishTime",-1),("PM25",sort_code)])
		space = data_list[0]["County"]
		values["pm25"] = data_list[0]["PM25"]
	elif handle_code == "UVI":
		data_list = collect.find().sort([("PublishTime",-1),("UVI",sort_code)])
		space = data_list[0]["County"]
		values["uvi"] = data_list[0]["UVI"]
	else: #temperature
		now_time = datetime.now()
		data_list = collect.find({'endTime': {'$gt': now_time},'startTime': {'$lt': now_time}}).sort([("PublishTime",-1),("temperature",sort_code)])
		space = data_list[0]["locationName"]
		values["temperature"] = data_list[0]["temperature"]
	
	return values, space
	
if __name__ == "__main__":
	handle_code = "UVI"
	HL = "L"
	values, space = get_most(handle_code,HL)
	print(values)
	print(space)