# -*- coding: utf-8 -*-
import urllib.request
import json
import os
import datetime as DT
from datetime import datetime
from pymongo import MongoClient

from sensor_config import *

def parse_json_data(pure_data):
	location = pure_data['records']['location']
	Location_list = {}
	for L in location:
		Location_list[L['locationName']] = {}
		for element in L['weatherElement']:
			for E in element['time']:
				end_time = datetime.strptime(E['endTime'], "%Y-%m-%d %H:%M:%S")
				if( end_time not in Location_list[L['locationName']] ):
					Location_list[L['locationName']][end_time] = {}
				Location_list[L['locationName']][end_time][element['elementName']] = E['parameter']['parameterName']
	return Location_list

def grab_data():
	Data_set = "F-C0032-001"
#connect to cwb api
	urll = 'http://opendata.cwb.gov.tw/api/v1/rest/datastore/'+Data_set+'?'
	target_url = urllib.request.Request(urll+'sort=time')

	target_url.add_header( 'Authorization' , weather_token)
	fp = urllib.request.urlopen(target_url)
	pure_data = json.loads(fp.read().decode('utf-8'))
	fp.close()
	
	data_list = parse_json_data(pure_data)
	
	new_data_list = []
	for location in data_list:
		item_list = data_list[location]
		for time in item_list:
			item = item_list[time]
			#print(item)
			data = {}
			data['locationName'] = location
			data['endTime'] = time
			data['startTime'] = time - DT.timedelta(hours=12)
			data['temperature'] = ( int(item['MaxT']) + int(item['MinT']) )/2
			data['rainfull_prob'] = int(item['PoP'])
			data['Wx'] = item['Wx']
			new_data_list.append(data)
	
	db_url = "{host}:27017".format(host=mongo_host)
	db_name = 'bot'
	client = MongoClient(db_url,  27017)
	db = client['bot']
	collect = db['weather_data']
	for data in new_data_list:
		upflag = collect.find_one_and_update({'endTime':data['endTime'],"locationName":data['locationName']}, { '$set' : { "temperature": data['temperature'], "rainfull_prob": data['rainfull_prob'], "Wx": data['Wx']}  }  )
		if upflag == None:
			collect.insert_one(data)
	return data_list
	
if __name__ == "__main__":
	data_list = grab_data()
	print (data_list["新竹市"])

