# encoding=utf-8
from pprint import pprint
import urllib.request
import urllib.parse
import json
import os
from datetime import datetime #datetime.datetime

def parse_json_data(pure_data):
	location = pure_data['records']['location']
	Location_list = {}
	for L in location:
		Location_list[L['locationName']] = {}
		for element in L['weatherElement']:
			for E in element['time']:
				start_time = datetime.strptime(E['startTime'], "%Y-%m-%d %H:%M:%S")
				if( start_time not in Location_list[L['locationName']] ):
					Location_list[L['locationName']][start_time] = {}
					end_time = datetime.strptime(E['endTime'], "%Y-%m-%d %H:%M:%S")
					Location_list[L['locationName']][start_time]['endTime'] = end_time
				Location_list[L['locationName']][start_time][element['elementName']] = E['parameter']['parameterName']
	return Location_list

def grab_data(Data_set,Location_name):
	#Data_set = input("請輸入資料集編號: ")
	#Location_name = input("請輸入地點(預設全選): ")

#connect to cwb api
	urll = 'http://opendata.cwb.gov.tw/api/v1/rest/datastore/'+Data_set+'?'
	Location_name = Location_name.strip()
	if Location_name:
		urll = urll+'locationName='
		target_url = urllib.request.Request(urll+ urllib.parse.quote(Location_name, safe='')+'&sort=time')
	else:
		target_url = urllib.request.Request(urll+ urllib.parse.quote(Location_name, safe='')+'sort=time')

	with open("token.txt","r") as token_file:
		token = token_file.readline().rstrip('\n')
	target_url.add_header( 'Authorization' , token)
	fp = urllib.request.urlopen(target_url)
	pure_data = json.loads(fp.read().decode('utf-8'))
	fp.close()

	with open("output.json","w") as file:
		pprint(pure_data,file)

	data_list = parse_json_data(pure_data)
	#print(data_list)

	with open("output.dat","w") as file:
		pprint(data_list,file)

	return data_list
	
if __name__ == "__main__":
	Data_set = "F-C0032-001"
	Location_name = "新竹市"
	data_list = grab_data(Data_set,Location_name)
	for data in data_list["新竹市"]:
		print (data)

