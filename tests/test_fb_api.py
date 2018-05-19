# -*- coding: utf-8 -*-

import sys
import os
PWD = os.getcwd()
sys.path.append(PWD)

import unittest

class FBApiTest(unittest.TestCase):
    def test_external_api(self):
        from fb_api.external_api import get_area
        
        location = {}
        location['lat'] = 25.0339639
        location['long'] = 121.5644722
        assertIsNotEqual(get_area(location), ("不知道",""))
        
if __name__ == "__main__":
    unittest.main()
