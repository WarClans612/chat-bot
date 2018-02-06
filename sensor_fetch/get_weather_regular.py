# -*- coding: utf-8 -*-
import urllib.request
import json
import os
import datetime as DT
from datetime import datetime
from pymongo import MongoClient

from sensor_config import *

def parse_json_data(raw_data):
    locations = raw_data['records']['location']
    raw_weather = {}
    for location in locations:
        raw_weather[location['locationName']] = {}
        for element in location['weatherElement']:
            for timestamp_entry in element['time']:
                end_time = datetime.strptime(timestamp_entry['endTime'], "%Y-%m-%d %H:%M:%S")
                if( end_time not in raw_weather[location['locationName']] ):
                    raw_weather[location['locationName']][end_time] = {}
                raw_weather[location['locationName']][end_time][element['elementName']] = timestamp_entry['parameter']['parameterName']

    weather_data = list()
    for location in raw_weather:
        location_data = raw_weather[location]
        for time in location_data:
            item = location_data[time]
            data = {}
            data['locationName'] = location
            data['endTime'] = time
            data['startTime'] = time - DT.timedelta(hours=12)
            data['MaxT'] = int(item['MaxT'])
            data['MinT'] = int(item['MinT'])
            data['temperature'] = ( int(item['MaxT']) + int(item['MinT']) )/2
            data['rainfull_prob'] = int(item['PoP'])
            data['Wx'] = item['Wx']
            weather_data.append(data)
    return weather_data

def grab_data():

    Data_set = "F-C0032-001"
    url = 'http://opendata.cwb.gov.tw/api/v1/rest/datastore/{Data_set}?sort=time'.format(Data_set=Data_set)
    request = urllib.request.Request(url)

    request.add_header( 'Authorization' , weather_token)
    with urllib.request.urlopen(request) as response:
        raw_data = json.loads(response.read().decode('utf-8'))

    weather_data = parse_json_data(raw_data)
    
    db_url = "{host}:27017".format(host=mongo_host)
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client['bot']
    collect = db['raw_weather']
    for data in weather_data:
        upflag = collect.find_one_and_update({'endTime':data['endTime'],"locationName":data['locationName']}, { '$set' : { "temperature": data['temperature'], "rainfull_prob": data['rainfull_prob'], "Wx": data['Wx']}  }  )
        if upflag == None:
            collect.insert_one(data)
    return weather_data
    
if __name__ == "__main__":
    weather_data = grab_data()
    print (weather_data["新竹市"])

