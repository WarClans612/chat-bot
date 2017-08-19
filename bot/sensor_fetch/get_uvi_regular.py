import urllib.request
import json
import os
from datetime import datetime
import pymongo
from pymongo import MongoClient

def grab_data():

#connect to cwb api
	urll = 'http://opendata.epa.gov.tw/ws/Data/UV/?$format=json'
	fp = urllib.request.urlopen(urll)
	data_list = json.loads(fp.read().decode('utf-8'))
	fp.close()
	
	return data_list

def save_uvi():
	data_list = grab_data()
	print(data_list)
	new_data_list = []
	for i in data_list:
		time = datetime.strptime(i['PublishTime'], "%Y-%m-%d %H:%M")
		data = {}
		data['County'] = i['County']
		data['UVI'] = i['UVI']
		data['PublishTime'] = time
		data['SiteName'] = i['SiteName']
		data['WGS84Lon'] = i['WGS84Lon']
		data['WGS84Lat'] = i['WGS84Lat']
		new_data_list.append(data)
	
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client[ 'bot']
	collect = db['uvi_data']
	collect.insert(new_data_list)
	
	return time
	
if __name__ == "__main__":
	save_uvi()