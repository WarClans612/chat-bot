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

if __name__ == "__main__":
    unittest.main()
