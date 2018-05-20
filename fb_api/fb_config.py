from bot import bot_config

MONGO_HOST = bot_config.db_url
MONGO_PORT = 27017
MONGO_DBNAME = bot_config.db_name
USER_INFO = 'user_information'
weighting_method = 'fre_prob'


'''
    Value below is used to contain the important config file for FB.
    Usually this data is not shared publicly.
    Therefore, the value should be changed first before usage
'''
VERIFICATION_CODE = 'unknown'
ACCESS_TOKEN = 'unknown'
Google_Maps_Geocoding_API_key = 'unknown'