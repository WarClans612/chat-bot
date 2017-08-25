import urllib.request
import json
import os
from datetime import datetime
import pymongo
from pymongo import MongoClient

def grab_data():

#connect to cwb api
	urll = 'http://opendata2.epa.gov.tw/AQI.json'
	fp = urllib.request.urlopen(urll)
	data_list = json.loads(fp.read().decode('utf-8'))
	fp.close()
	
	return data_list

def save_pm25():
	data_list = grab_data()
	new_data_list = []
	for i in data_list:
		time = datetime.strptime(i['PublishTime'], "%Y-%m-%d %H:%M")
		data = {}
		data['County'] = i['County']
		if i['PM2.5'] == "ND" or i['PM2.5'] == "":
			data['PM25'] = 0
		else:
			data['PM25'] = int(i['PM2.5'])
		print(data['PM25'])
		data['PublishTime'] = time
		data['SiteName'] = i['SiteName']
		new_data_list.append(data)
	
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client[ 'bot']
	collect = db['pm25_data']
	collect.insert(new_data_list)
	
	return time
	
if __name__ == "__main__":
	save_pm25()