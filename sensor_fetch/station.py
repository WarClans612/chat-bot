# -*- coding: utf-8 -*-
from datetime import datetime
from sensor_fetch.util import SensorUtil

def parse_json_data(raw_data):
    pm25_station_data = []
    for item in raw_data["pm25"]:
        data = {}
        data['Lon'] = float(item['TWD97Lon'])
        data['Lat'] = float(item['TWD97Lat'])
        data['SiteName'] = item['SiteName']
        pm25_station_data.append(data)
    
    uvi_station_data = []
    for item in raw_data["uvi"]:
        data = {}
        Lon = item['WGS84Lon'].split(',')
        Lat = item['WGS84Lat'].split(',')
        data['Lon'] = float(Lon[0]) + float(Lon[1])/100 + float(Lon[2])/10000
        data['Lat'] = float(Lat[0]) + float(Lat[1])/100 + float(Lat[2])/10000
        data['SiteName'] = item['SiteName']
        uvi_station_data.append(data)
    station = {}
    station["pm25"] = pm25_station_data
    station["uvi"] = uvi_station_data
    return station

def fetch():
    """
    Fetch PM2.5 station data and uvi station data

    API:
    PM2.5: http://opendata.epa.gov.tw/ws/Data/AQXSite/
    UVI: http://opendata.epa.gov.tw/ws/Data/UV/

    Returns:
        station_data: a dict contain uvi and pm25 stations
        Format:
            {
                "uvi": [
                    {
                        "Lon": 120,
                        "Lat": 25,
                        "SiteName": "SiteA"
                    },
                    ...
                ],
                "pm25" [
                    {
                        "Lon": 125,
                        "Lat": 23,
                        "SiteName": "SiteB"
                    },
                    ...
                ]
            }
    """
    client = SensorUtil()
    raw_data = {}
    raw_data["pm25"] = client.grab_raw_data_from_url('http://opendata.epa.gov.tw/ws/Data/AQXSite/?$format=json')
    raw_data["uvi"] = client.grab_raw_data_from_url('http://opendata.epa.gov.tw/ws/Data/UV/?$format=json')
    if raw_data["pm25"] is None or raw_data["uvi"] is None:
        return None
    station = parse_json_data(raw_data)
    return station

def save(data):
    """
    This function should store the input data into database
    Return true when data is stored successfully
    """
    if data is None:
        return False
    client = SensorUtil()
    pm25_status = client.save_data_into_db(data['pm25'], 'pm25_station_data')
    uvi_status = client.save_data_into_db(data['uvi'], 'uvi_station_data')
    if pm25_status and uvi_status:
        return True
    else:
        return False
