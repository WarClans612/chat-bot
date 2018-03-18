import sys
import os
PWD = os.getcwd()
sys.path.append(PWD)

import unittest

class ConfigTest(unittest.TestCase):
    """
    The sensor_config.py should contain following settings
    """
    def setUp(self):
        from sensor_fetch import sensor_config
        self.config = sensor_config

    def test_weather_token(self):
        self.assertIsInstance(self.config.weather_token,str)

    def test_host(self):
        self.assertIsInstance(self.config.host,str)

class MongoDBTest(unittest.TestCase):
    """
    Test connection of MongoDB using pymongo
    """
    def setUp(self):
        from sensor_fetch import sensor_config
        self.host = sensor_config.host

    def test_connect(self):
        from pymongo import MongoClient
        self.client = MongoClient(self.host,serverSelectionTimeoutMS=5000)
        self.assertIsInstance(self.client.server_info(), dict)

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
            self.assertIn(key, rainfall_data)

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

if __name__ == "__main__":
    unittest.main()