# -*- coding: utf-8 -*-
from datetime import datetime
from sensor_fetch.util import grab_raw_data_from_url

def parse_json_data(raw_data):
    uvi_data = []
    for item in raw_data:
        data = {}
        if item['UVI'] == "":
            data['UVI'] = 0.0
        elif float(item['UVI']) > 0:
            data['UVI'] = float(item['UVI'])
        else:
            data['UVI'] = 0.0
        data['County'] = item['County']
        data['PublishTime'] = datetime.strptime(item['PublishTime'], "%Y-%m-%d %H:%M")
        data['SiteName'] = item['SiteName']
        data['WGS84Lon'] = item['WGS84Lon']
        data['WGS84Lat'] = item['WGS84Lat']
        uvi_data.append(data)
    return uvi_data

def fetch():
    """
    Fetch data from http://opendata.epa.gov.tw/ws/Data/UV/

    Returns:
        uvi_data: a list of UVI data
        Format:
        [
            {
                'UVI': ,
                'County': ,
                'PublishTime': ,
                'SiteName': ,
                'WGS84Lon': ,
                'WGS84Lat: '
            },
            ...
        ]
    """
    raw_data = grab_raw_data_from_url('http://opendata.epa.gov.tw/ws/Data/UV/?$format=json')
    uvi_data = parse_json_data(raw_data)
    return uvi_data

def save(data):
    """
    This function should store the input data into database
    Return true when data is stored successfully
    """
    pass

def get(name):
    """
    This function will return the UVI value in this hour by querying the database

    If the data is outdated, call the fetch() and save(), then do the query again

    Args:
        name: The name can be the Site name or County

    Return:
        UVI value in this hour, ``None`` when the name can't be recongnized.`
    """
    pass
