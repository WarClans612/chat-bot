# -*- coding: utf-8 -*-
import urllib.request
import json
import datetime as DT
from sensor_fetch import sensor_config
from datetime import datetime
from sensor_fetch.util import save_weather_to_db

def grab_raw_data():
    Data_set = "F-C0032-001"
    url = 'http://opendata.cwb.gov.tw/api/v1/rest/datastore/{Data_set}?sort=time'.format(Data_set=Data_set)
    request = urllib.request.Request(url)

    request.add_header( 'Authorization' , sensor_config.weather_token)
    with urllib.request.urlopen(request) as response:
        raw_data = json.loads(response.read().decode('utf-8'))
    return raw_data

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

    weather_data = []
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

def fetch():
    """
    Fetch "F-C0032-001" dataset from http://opendata.cwb.gov.tw
    Returns:
        weather_data: a list of weather data
            [
                {
                    'locationName': ,
                    'endTime': ,
                    'startTime': ,
                    'MaxT':,
                    'MinT': ,
                    'temperature':,
                    'rainfull_prob':,
                    'Wx':
                },
                ...
            ]
    """
    raw_data = grab_raw_data()
    weather_data = parse_json_data(raw_data)
    return weather_data

def save(data):
    """
    This function should store the input data into database
    Return true when data is stored successfully
    """
    return save_weather_to_db(data)

def get(name, time='now'):
    """
    This function will return the weather data according to the ``time``,
    the weather data is the result of querying the database.

    If the data is outdated, call the fetch() and save(), then do the query again.

    Args:
        name: location name of the weather

    Return:
        weather data now or in future ``time`` hours
    """
    pass