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

def get_weather(Location_name,time):
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client['bot']
	collect = db['weather_data']
	
	if time == "now":
		now_time = datetime.now()
		item = collect.find_one({'endTime': {'$gt': now_time},'startTime': {'$lt': now_time},'locationName':Location_name})
	else:
		now_time = datetime.now()
		now_day = datetime(now_time.year, now_time.month, now_time.day, 12, 0, 0, 0)
		next_day = now_day + DT.timedelta(days=1)
		item = collect.find_one({'endTime': {'$gt': next_day},'startTime': {'$lt': next_day},'locationName':Location_name})
	
	return item
	
if __name__ == "__main__":
	Location_name = "新竹市"
	item = get_weather(Location_name)
	print(item)
	

