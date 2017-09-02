import urllib.request
import json
import os
import datetime as DT
from datetime import datetime
import pymongo
from pymongo import MongoClient

recommend_mapping = {"臺東縣": "太麻里"}

def get_where_rainbow(slots):
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client['bot']
	collect = db["weather_data"]
	
	time = slots["time"]
	if time == "now":
		now_time = datetime.now()
		time_we_want = now_time
	else:
		now_time = datetime.now()
		now_day = datetime(now_time.year, now_time.month, now_time.day, 12, 0, 0, 0)
		next_day = now_day + DT.timedelta(days=1)
		time_we_want = next_day
	
	data_list1 = collect.find({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want}, 'Wx': "晴午後短暫陣雨"})
	data_list2 = collect.find({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want}, 'Wx': "晴午後短暫雷陣雨"})
	county_list = []
	for data in data_list1:
		county_list.append(data['locationName'])
	for data in data_list2:
		county_list.append(data['locationName'])
	print(county_list)
	return county_list
	
def if_rainbow(slots):
	rainbow_list = ["晴午後短暫陣雨","晴午後短暫雷陣雨"]
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client['bot']
	collect = db["weather_data"]
	
	Location_name = slots["space"]
	
	time = slots["time"]
	if time == "now":
		now_time = datetime.now()
		time_we_want = now_time
	else:
		now_time = datetime.now()
		now_day = datetime(now_time.year, now_time.month, now_time.day, 12, 0, 0, 0)
		next_day = now_day + DT.timedelta(days=1)
		time_we_want = next_day
		
	item = collect.find_one({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want},'locationName':Location_name})
	wx = item["Wx"]
	
	if wx in rainbow_list :
		result = True
	else:
		result = False
	
	return result, wx
	
def get_where_sunrise():
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client['bot']
	collect = db["weather_data"]
	
	now_time = datetime.now()
	if now_time.hour < 6:
		time_we_want = datetime(now_time.year, now_time.month, now_time.day, 6, 1, 0, 0)
	else:
		next_day = now_time + DT.timedelta(days=1)
		time_we_want = datetime(next_day.year, next_day.month, next_day.day, 6, 1, 0, 0)
		
	data_list = []
	data_list.extend( collect.find({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want}, 'Wx': "晴午後短暫陣雨"}) )
	data_list.extend( collect.find({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want}, 'Wx': "晴午後短暫雷陣雨"}) )
	data_list.extend( collect.find({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want}, 'Wx': "晴天"}) )
	data_list.extend( collect.find({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want}, 'Wx': "晴時多雲"}) )
	
	county_list = []
	for data in data_list:
		county_list.append(data['locationName'])
	
	recommend_list = []
	for data in data_list:
		if data['locationName'] in recommend_mapping :
			recommend_list.append( recommend_mapping[ data['locationName'] ] )

		
		
	return recommend_list, county_list
	
def if_sunrise(slots):
	sunlist = ["晴午後短暫陣雨","晴午後短暫雷陣雨","晴天","晴時多雲"]
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client['bot']
	collect = db["weather_data"]
	
	Location_name = slots["space"]
	
	now_time = datetime.now()
	if now_time.hour < 6:
		time_we_want = datetime(now_time.year, now_time.month, now_time.day, 6, 1, 0, 0)
	else:
		next_day = now_time + DT.timedelta(days=1)
		time_we_want = datetime(next_day.year, next_day.month, next_day.day, 6, 1, 0, 0)
		
	item = collect.find_one({'endTime': {'$gt': time_we_want},'startTime': {'$lt': time_we_want},'locationName':Location_name})
	wx = item["Wx"]
	
	if wx in sunlist :
		result = True
	else:
		result = False
	
	return result, wx
	
	

if __name__ == "__main__":
	# slots = {}
	# slots["time"] = "now"
	# get_where_rainbow(slots)
	
	# recommend_list, county_list = get_where_sunrise()
	# print(recommend_list)
	# print(county_list)
	
	slots = {}
	slots["space"] = "臺東縣"
	result, wx = if_sunrise(slots)
	print(result)
	print(wx)
	