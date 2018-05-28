import os
'''
    This file contains file config that will be imported by each config file
    (DB location, PORT, and NAME)
    Each module has its own config file
    In this chatbot, most data in module config file is imported from this file
'''

HOST = os.environ['DB_HOST'] #'127.0.0.1'
PORT = int(os.environ['DB_PORT']) #27017
URL = HOST + ':' + str(PORT)
DB_NAME = 'bot'
