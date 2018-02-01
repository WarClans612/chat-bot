import urllib.request
import json
from datetime import datetime
from pymongo import MongoClient
from sensor_config import *

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
	print(data_list)
	new_data_list = []
	for i in data_list:
		data = {}
		data['Lon'] = float(i['TWD97Lon'])
		data['Lat'] = float(i['TWD97Lat'])
		data['SiteName'] = i['SiteName']
		new_data_list.append(data)
	
	db_url = "{host}:27017".format(host=mongo_host)
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client[ 'bot']
	db.drop_collection('pm25_station_data')
	collect = db['pm25_station_data']
	collect.insert(new_data_list)
	
def get_uvi_station_location():
	data_list = grab_uvi_station()
	print(data_list)
	new_data_list = []
	for i in data_list:
		data = {}
		Lon = i['WGS84Lon']
		Lat = i['WGS84Lat']
		data['Lon'] = float(Lon.split(",")[0])+float(Lon.split(",")[1])/100+float(Lon.split(",")[2])/10000
		data['Lat'] = float(Lat.split(",")[0])+float(Lat.split(",")[1])/100+float(Lat.split(",")[2])/10000
		data['SiteName'] = i['SiteName']
		new_data_list.append(data)
	
	db_url = "{host}:27017".format(host=mongo_host)
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client[ 'bot']
	db.drop_collection('uvi_station_data')
	collect = db['uvi_station_data']
	collect.insert(new_data_list)

	
if __name__ == "__main__":
	get_pm25_station_location()
	get_uvi_station_location()
