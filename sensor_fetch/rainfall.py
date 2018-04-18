# -*- coding: utf-8 -*-
from datetime import datetime
from sensor_fetch.util import grab_raw_data_from_url
from sensor_fetch.util import save_data_into_db

def parse_json_data(raw_data):
    rainfall_data = []
    for item in raw_data:
        data = dict()
        data['County'] = item['County']
        data['rainfall1hr'] = float(item['Rainfall1hr'])
        data['rainfall3hr'] = float(item['Rainfall3hr'])
        data['rainfall6hr'] = float(item['Rainfall6hr'])
        data['rainfall12hr'] = float(item['Rainfall12hr'])
        data['rainfall24hr'] = float(item['Rainfall24hr'])
        data['SiteName'] = item['SiteName']
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
                'rainfall3hr': ,
                'rainfall6hr': ,
                'rainfall12hr': ,
                'rainfall24hr': ,
                'SiteName: '
                'PublishTime':
            },
            ...
        ]
    """
    raw_data = grab_raw_data_from_url('http://opendata.epa.gov.tw/ws/Data/RainTenMin/?format=json')
    rainfall_data = parse_json_data(raw_data)
    return rainfall_data

def save(data):
    """
    This function should store the input data into database
    Return true when data is stored successfully
    """
    return save_data_into_db(data, 'rainfall_data')

def get(name, hours=1):
    """
    This function will return the rainfall data in past ``hours`` hour(s), 
    the rainfall data is the result of querying the database.

    If the results of rainfall in ``name`` location are more than one, pick the first 
    one as the result.

    If the data is outdated, call the fetch() and save(), then do the query again.

    Args:
        name: The name can be the Site name or County

    Return:
        rainfall in past ``hours`` hour(s), ``None`` when the name can't be recongnized 
        or the ``hours`` is not supported.`
    """
    pass
