import urllib.request
import json
import os
from datetime import datetime
import pymongo
from pymongo import MongoClient

def get_rainfall(Location_name):
    db_url = "127.0.0.1:27017"
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client[ 'bot']
    collect = db['rainfall_data']
    
    data_list = collect.find({"County": Location_name}).sort([("PublishTime",-1)])
    
    item = data_list[0]
    
    return item['rainfall1hr'], item['rainfall24hr']
    
    
if __name__ == "__main__":
    rainfall1hr, rainfall24hr = get_rainfall("新竹市")
    print(rainfall1hr)
    print(rainfall24hr)
