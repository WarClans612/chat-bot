import os
import config

MONGO_HOST = config.URL
MONGO_PORT = config.PORT
MONGO_DBNAME = config.DB_NAME
USER_INFO = 'user_information'
weighting_method = 'fre_prob'


'''
    Value below is used to contain the important config file for FB.
    Usually this data is not shared publicly.
    Therefore, the value should be changed first before usage
'''
VERIFICATION_CODE = os.environ['VERIFICATION_CODE']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
Google_Maps_Geocoding_API_key = os.environ['Google_Maps_Geocoding_API_key']