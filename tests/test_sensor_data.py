# -*- coding: utf-8 -*-

import sys
import os
PWD = os.getcwd()
sys.path.append(PWD)

import unittest

class SensorFetchTest(unittest.TestCase):
    def test_fetch_weather(self):
        weather_keys = ['locationName','endTime','startTime','MaxT','MinT','temperature','rainfull_prob','Wx']

        from sensor_fetch.weather import fetch
        weather_data = fetch()
        for key in weather_keys:
            self.assertIn(key,weather_data[0])

    def test_fetch_pm25(self):
        pm25_keys = ['PM25','County','PublishTime','SiteName']

        from sensor_fetch.pm25 import fetch
        pm25_data = fetch()
        for key in pm25_keys:
            self.assertIn(key, pm25_data[0])

    def test_fetch_uvi(self):
        uvi_keys = ['UVI','County','PublishTime','SiteName','WGS84Lon','WGS84Lat']

        from sensor_fetch.uvi import fetch
        uvi_data = fetch()
        for key in uvi_keys:
            self.assertIn(key, uvi_data[0])

    def test_fetch_rainfall(self):
        rainfall_keys = ['County','rainfall1hr','rainfall24hr','PublishTime']

        from sensor_fetch.rainfall import fetch
        rainfall_data = fetch()
        for key in rainfall_keys:
            self.assertIn(key, rainfall_data[0])

    def test_fetch_station_location(self):
        """
        Station data should be
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
        station_keys = ['Lon','Lat','SiteName']

        from sensor_fetch.station import fetch
        station_data = fetch()
        for sensor_type in ['uvi','pm25']:
            for key in station_keys:
                self.assertIn(key,station_data[sensor_type][0])

    def test_store_to_database(self):
        from sensor_fetch import pm25, rainfall, station, uvi, weather

        for sensor in [pm25,rainfall, station, uvi, weather]:
            data = sensor.fetch()
            self.assertTrue(sensor.save(data))

    def test_get_pm25(self):
        from sensor_fetch.pm25 import get

        #test get from site name
        self.assertIsNotNone(get('基隆'))
        #test get from county name
        self.assertIsNotNone(get('基隆市'))
