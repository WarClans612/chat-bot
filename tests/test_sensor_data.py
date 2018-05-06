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

    def test_get_uvi(self):
        from sensor_fetch.uvi import get

        #test get from site name
        self.assertIsNotNone(get('彰化'))
        #test get from county name
        self.assertIsNotNone(get('彰化縣'))

    def test_get_rainfall(self):
        from sensor_fetch.rainfall import get

        #test get from site name
        self.assertIsNotNone(get("臺灣大學"))
        #test get from County
        self.assertIsNotNone(get("臺北市"))
        #test get past 1 hours
        self.assertIsNotNone(get("臺北市", hours=1))
        #test get past 24 hours
        self.assertIsNotNone(get("臺北市", hours=24))

        #test result data type
        self.assertNotIsInstance(get("臺北市"), list)

    def test_get_weather(self):
        from sensor_fetch.weather import get

        self.assertIsNotNone(get("臺東縣"))

        self.assertIsNotNone(get("臺東縣", time=6))

        self.assertIsNotNone(get("臺東縣", time=12))

        self.assertIsNotNone(get("臺東縣", time=24))

        self.assertIsNotNone(get("臺東縣", time=36))

    def test_sensor_highest_value(self):
        from sensor_fetch.sensor_highest_value import sensor_highest_value
        
        #test for highest
        self.assertIsNotNone(sensor_highest_value("PM25", "H"))
        self.assertIsNotNone(sensor_highest_value("temperature", "H"))
        self.assertIsNotNone(sensor_highest_value("UVI", "H"))
        self.assertIsNotNone(sensor_highest_value("RAINFALL", "H"))
        
        #test for lowest
        self.assertIsNotNone(sensor_highest_value("PM25", "L"))
        self.assertIsNotNone(sensor_highest_value("temperature", "L"))
        self.assertIsNotNone(sensor_highest_value("UVI", "L"))
        self.assertIsNotNone(sensor_highest_value("RAINFALL", "L"))

    def test_location_of_sky_condition(self):
        from sensor_fetch.sky import location_of_sky_condition
        
        #Initializing test argument
        slots = {}
        slots["time"] = "now"
        
        self.assertIsNotNone(location_of_sky_condition("rainbow", slots))
        self.assertIsNotNone(location_of_sky_condition("sunrise", slots))
        self.assertIsNotNone(location_of_sky_condition("sunrise"))
        
    def test_on_sky(self):
        from sensor_fetch.sky import on_sky
        
        #Initializing test argument
        slots = {}
        slots["space"] = "臺東縣"
        slots["time"] = "now"
        
        self.assertIsNotNone(on_sky("rainbow", slots))
        self.assertIsNotNone(on_sky("sunrise", slots))

if __name__ == "__main__":
    unittest.main()
