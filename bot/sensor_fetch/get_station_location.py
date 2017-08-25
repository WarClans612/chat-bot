import urllib.request
import json
import os
from datetime import datetime
import pymongo
from pymongo import MongoClient

def grab_pm25_station():

#connect to cwb api
	urll = 'http://opendata.epa.gov.tw/ws/Data/AQXSite/?$format=json'
	fp = urllib.request.urlopen(urll)
	data_list = json.loads(fp.read().decode('utf-8'))
	fp.close()
	
	return data_list
	
def grab_uvi_station():

#connect to cwb api
	urll = 'http://opendata.epa.gov.tw/ws/Data/UV/?$format=json'
	fp = urllib.request.urlopen(urll)
	data_list = json.loads(fp.read().decode('utf-8'))
	fp.close()
	
	return data_list

def get_pm25_station_location():
	data_list = grab_pm25_station()
	new_data_list = []
	for i in data_list:
		data = {}
		data['Lon'] = float(i['TWD97Lon'])
		data['Lat'] = float(i['TWD97Lat'])
		data['SiteName'] = i['SiteName']
		new_data_list.append(data)
	
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client[ 'bot']
	db.drop_collection('pm25_station_data')
	collect = db['pm25_station_data']
	collect.insert(new_data_list)
	
def get_uvi_station_location():
	data_list = grab_uvi_station()
	new_data_list = []
	for i in data_list:
		data = {}
		Lon = i['WGS84Lon']
		Lat = i['WGS84Lat']
		data['Lon'] = float(Lon.split(",")[0])+float(Lon.split(",")[1])/100+float(Lon.split(",")[2])/10000
		data['Lat'] = float(Lat.split(",")[0])+float(Lat.split(",")[1])/100+float(Lat.split(",")[2])/10000
		data['SiteName'] = i['SiteName']
		new_data_list.append(data)
	
	db_url = "127.0.0.1:27017"
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client[ 'bot']
	db.drop_collection('uvi_station_data')
	collect = db['uvi_station_data']
	collect.insert(new_data_list)

	
if __name__ == "__main__":
	get_pm25_station_location()
	get_uvi_station_location()