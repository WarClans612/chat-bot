#!/usr/bin/python3.4
import os

db_url = "127.0.0.1:27017"
db_name = 'bot'

QAset = os.path.join(os.path.dirname(__file__), 'data/QAset.txt')
sensorQAset = os.path.join(os.path.dirname(__file__), 'data/sensor_QAset.txt')
iQAset = os.path.join(os.path.dirname(__file__), 'data/i_QAset.txt')

stopWordsDict = os.path.join(os.path.dirname(__file__), 'extra_dict/stop_words.txt')
idfFile = os.path.join(os.path.dirname(__file__), 'extra_dict/idf.txt.big')
twDict = os.path.join(os.path.dirname(__file__), 'extra_dict/zh-tw_dict.txt')
userDict = os.path.join(os.path.dirname(__file__), 'extra_dict/my_dict.txt')
locationDict = os.path.join(os.path.dirname(__file__), 'extra_dict/location_dict.txt')

segment_api_url = 'http://127.0.0.1:25555/segmentation/'

'''
    Value to control how easy to pass as qualified 
    when determining question type
    bot/method.py
'''
general_threshold = 0.6
sensor_threshold = 0.6
i_threshold = 0.6