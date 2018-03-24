# -*- coding: utf-8 -*-
from datetime import datetime
from sensor_fetch.util import grab_raw_data_from_url

def parse_json_data(raw_data):
    rainfall_data = []
    for item in raw_data:
        data = dict()
        data['County'] = item['County']
        data['rainfall1hr'] = float(item['Rainfall1hr'])
        data['rainfall24hr'] = float(item['Rainfall24hr'])
        data['PublishTime'] = datetime.strptime(item['PublishTime'], "%Y-%m-%d %H:%M:%S")
        rainfall_data.append(data)
    return rainfall_data

def fetch():
    """
    Fetch data from http://opendata.epa.gov.tw/ws/Data/RainTenMin/

    Returns:
        rainfall_data: a list of rainfall data
        Format:
        [
            {
                'County': ,
                'rainfall1hr': ,
                'rainfall24hr': ,
                'PublishTime':
            },
            ...
        ]
    """
    raw_data = grab_raw_data_from_url('http://opendata.epa.gov.tw/ws/Data/RainTenMin/?format=json')
    rainfall_data = parse_json_data(raw_data)
    return rainfall_data
