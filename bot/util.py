#!/usr/bin/python

from bot import bot_config
from pymongo import MongoClient

def connect_to_database():
    db_url = bot_config.db_url 
    db_name = bot_config.db_name
    client = MongoClient(db_url)
    db = client[db_name]
    return db