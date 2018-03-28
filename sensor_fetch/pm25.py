# -*- coding: utf-8 -*-
from datetime import datetime
from sensor_fetch.util import grab_raw_data_from_url

def parse_json_data(raw_data):
    pm25_data = []
    for item in raw_data:
        data = dict()
        if item['PM2.5'] in ["ND",""]:
            data['PM25'] = 0
        else:
            data['PM25'] = int(item['PM2.5'])
        data['County'] = item['County']
        data['PublishTime'] = datetime.strptime(item['PublishTime'], "%Y-%m-%d %H:%M")
        data['SiteName'] = item['SiteName']
        pm25_data.append(data)
    return pm25_data

def fetch():
    """
    Fetch data from http://opendata2.epa.gov.tw/AQI.json

    Returns:
        pm25_data: a list of pm25 data
        Format:
        [
            {
                'PM25': ,
                'County': ,
                'PublishTime': ,
                'SiteName':
            },
            ...
        ]
    """
    raw_data = grab_raw_data_from_url('http://opendata2.epa.gov.tw/AQI.json')
    pm25_data = parse_json_data(raw_data)
    return pm25_data

def save(data):
    """
    This function should store the input data into database
    Return true when data is stored successfully
    """
    pass

def get(name):
    """
    This function will return the PM25 value in this hour by querying the database

    If the data is outdated, call the fetch() and save(), then do the query again

    Args:
        name: The name can be the Site name or County

    """
    pass