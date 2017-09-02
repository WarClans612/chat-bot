import urllib.request
import json
import os
from datetime import datetime
import pymongo
from pymongo import MongoClient

def grab_data():

#connect to cwb api
	urll = 'http://opendata.epa.gov.tw/ws/Data/RainTenMin/?$format=json'
	fp = urllib.request.urlopen(urll)
	data_list = json.loads(fp.read().decode('utf-8'))
	fp.close()
	
	return data_list

def save_rainfall():
	county_list = []
	data_list = grab_data()
	new_data_list = []
	for i in data_list:
		county = i['County']   
		if county not in county_list:
			county_list.append(county)
			data = {}  
			time = datetime.strptime(i['PublishTime'], "%Y-%m-%d %H:%M:%S")
			data['County'] = county
			data['rainfall1hr'] = float(i['Rainfall1hr'])
			data['rainfall24hr'] = float(i['Rainfall24hr'])
			data['PublishTime'] = time
			print(data)
			new_data_list.append(data)
	
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client[ 'bot']
	collect = db['rainfall_data']
	collect.insert(new_data_list)
	
	return time
	
if __name__ == "__main__":
	save_rainfall()