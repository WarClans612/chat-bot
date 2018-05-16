# -*- coding: utf-8 -*-
"""
{"WEATHER": "天氣" , "RAIN": "降雨" , "PM25": "PM2.5" ,"GOOUT": "戶外資訊" ,"UVI": "紫外線指數"}
"""
import jieba
import jieba.analyse
from datetime import datetime
import urllib.request
import urllib.parse
import sys
import re
from pymongo import MongoClient
from bot import bot_config
from bot import util
from bot.bot_answer_code import *
from sensor_fetch import sensor_highest_value
from sensor_fetch import sky

topK = 20
withWeight = False
allowPOS = ()
default_message = "找不到符合的答案"

def segment(question):
    '''
        This function return the question in segmented list
        Possible output ['今天' ,'臺南', '溫度']
    '''
    return jieba.analyse.extract_tags(question, topK=topK, withWeight=withWeight, allowPOS=allowPOS)

def sensor_handler(types, handle_code, slots):
    '''
        This function return answer sentences that is wanted
        types --> normal, subscription
    '''
    temperature = 0
    rainfull_prob = 0
    air_quality = 0
    uvi = 0
    rainfall1hr = 0
    rainfall24hr = 0
    
    #Get answer code for the corresponding handle
    if handle_code == "WEATHER" :
        temperature, rainfull_prob, answer_code = get_weather_answer_code(slots)
    elif handle_code == "RAIN":
        temperature, rainfull_prob, answer_code = get_rain_answer_code(slots)
    elif handle_code == "PM25":
        air_quality, answer_code = get_pm25_answer_code(slots)
    elif handle_code == "GOOUT":
        air_quality, temperature, rainfull_prob, uvi, answer_code = get_goout_answer_code(slots)
    elif handle_code == "UVI":
        uvi, answer_code = get_uvi_answer_code(slots)
    elif handle_code == "RAINFALL" and types == "normal":
        rainfall1hr, rainfall24hr, answer_code = get_rainfall_answer_code(slots)
    else: 
        print("[err: no such handle_code -- ",handle_code," ]")
        return default_message
        
    if answer_code == 0:
        return '0'

    #Connect to DB
    db = util.connect_to_database()
    A_template = db.handle_table.find_one({'handle_code':handle_code, 'answer_code':answer_code })['A_template']
    answer = A_template
    
    #Preparation to replace answer template with the data
    if types == "normal":
        replace_mapping = {"#temperature#" : temperature , "#rainfull_prob#" : rainfull_prob , "#pm25#" : air_quality , "#uvi#" : uvi, "#rainfall1hr#" : rainfall1hr , "#rainfall24hr#" : rainfall24hr}
    elif types == "subscription":
        replace_mapping = {"#temperature#" : temperature , "#rainfull_prob#" : rainfull_prob , "#pm25#" : air_quality , "#uvi#" : uvi}
    else:
        return None
    
    #Replacing answer template with data
    for pattern in replace_mapping :
        if re.search(pattern, A_template) != None:
            answer = re.sub(pattern, str(replace_mapping[pattern]), answer)
    if "time" in slots:
        if slots["time"] == "now":
            time_str = "目前"
        else:
            time_str = "明天"
    else:
        time_str = "目前"
    answer = re.sub("#time#", str(time_str), answer)
    answer = re.sub("#space#", str(slots["space"]), answer)
    
    #Special condition when the types is subscription
    if types == "subscription":
        if handle_code == "RAIN" and answer_code<=1:
            answer = None
        elif handle_code == "PM25" and answer_code <= 2 :
            answer = None
        elif handle_code == "UVI" and answer_code <= 2 :
            answer = None
    
    return answer

def i_handler(question_num,handle_code,HL,slots):
    '''
        This function return answer sentences that is wanted
        handle_code --> RAINBOW, SUNRISE
    '''
    #Returning answer correspond to handle_code, and try to get the most value of other data handle code is invalid
    if handle_code == "RAINBOW":
        if slots.get("time"):
            if slots["time"] == "now":
                time = "目前"
            else:
                time = "明天"
        else:
            time = "目前"
            slots["time"] = "now"
            
        if slots.get("space"):
            #Initial checking for answer availability
            value = sky.on_sky("rainbow", slots)
            if value is None:
                return default_message
            result, wx = value
            if result:
                answer = slots["space"]+time+"天氣"+wx+" 有機會看到彩虹喔!"
            else:
                answer = slots["space"]+time+"天氣"+wx+" 不太有機會看到彩虹"
            return answer
        else:
            county_list = sky.location_of_sky_condition("rainbow", slots)
            num = len(county_list)
            if num == 0:
                answer = "下雨過後出太陽才能看到彩虹 "+time+"各地都沒什麼機會看到彩紅耶,好可惜"
            elif num == 1:
                answer = time+"只有"+county_list[0]+"有機會看到喔!"
            else:
                answer = time+"在"+",".join(county_list)+"都有機會看到,祝你幸運~"
            return answer
    elif handle_code == "SUNRISE":
        if slots.get("space"):
            #Initial checking for answer availability
            value = sky.on_sky("sunrise", slots)
            if value is None:
                return default_message
            result, wx = value
            if result:
                answer = slots["space"]+"明天清晨天氣"+wx+" 有機會看到日出喔!"
            else:
                answer = slots["space"]+"明天清晨天氣"+wx+" 不太有機會看到日出"
        else:
            recommend_list, county_list = sky.location_of_sky_condition("sunrise")
            if len(recommend_list) != 0:
                answer = "推薦可以到"+"、".join(recommend_list)+"欣賞日出,明天清晨天氣不錯"
            elif len(county_list) !=0:
                answer = "明天清晨天氣較佳有機會欣賞日出的縣市如下:"+"、".join(county_list)+" 祝您有個愉快的一天"
            else:
                answer = "明天清晨全臺天氣都不佳，可能比較沒有機會看到日出喔"
        return answer
    else:
        values,space = sensor_highest_value.sensor_highest_value(handle_code,HL)
        
        db = util.connect_to_database()
        answer = db.answer_table.find_one({'question_num':question_num})['answer']
        
        temperature = values["temperature"]
        air_quality = values["PM25"]
        uvi = values["UVI"]
        rainfall24hr = values["rainfall24hr"]
        
        #Preparation to replace answer template with the data
        replace_mapping = {"#temperature#" : temperature , "#pm25#" : air_quality , "#uvi#" : uvi, "#rainfall24hr#" : rainfall24hr}
        #Replacing answer template with data
        for pattern in replace_mapping :
            if re.search(pattern, answer) != None:
                answer = re.sub(pattern, str(replace_mapping[pattern]), answer)
        answer = re.sub("#space#", space, answer)
        return answer
    
def get_answer(question_num, slots):
    '''
        This function return answer sentence from the given question_num
    '''
    db = util.connect_to_database()
    #Try to find the wanted entry
    question_table = db["question_table"].find_one({'question_num':question_num})
    #If no entry is found, return default message
    if question_table is None:
        return default_message

    handle_code = question_table['handle_code']
    type = question_table['type']
    
    #Check answer type and return as needed
    #Sky condition
    if type == "i":
        HL = question_table['HL_code']
        answer = i_handler(question_num, handle_code, HL, slots)
    #General QA
    elif type == "general":
        answer_table = db["answer_table"].find_one({'question_num':question_num})
        answer = answer_table['answer']
    #Sensor Data Related QA
    else:
        answer = sensor_handler("normal", handle_code, slots)
    return answer
    
def get_location_sQA_answer(question_num,slots,location):
    db = util.connect_to_database()
    handle_code = db.question_table.find_one({'question_num':question_num})['handle_code']
    
    if handle_code in ["PM25","UVI"]:
        slots["SiteName"] = nearest_station(handle_code, location)
        slots["space"] = "您最接近{station}測站,".format(station=slots["SiteName"])

    answer = sensor_handler(handle_code,slots)
    return answer

def nearest_station(handle_code, location):
    user_lon = location['long']
    user_lat = location['lat']

    db = util.connect_to_database()
    
    if handle_code == "PM25":
        station_list = db['pm25_station_data'].find()
    else : # "UVI"
        station_list = db['uvi_station_data'].find()
    
    first = station_list[0]
    SiteName = first["SiteName"]
    min_D = haversine(user_lon, user_lat, first["Lon"], first["Lat"])
    for station in station_list:
        D = haversine(user_lon, user_lat, station["Lon"], station["Lat"])
        if D < min_D:
            min_D = D
            SiteName = station["SiteName"]
    return SiteName
    
def haversine(lon1, lat1, lon2, lat2):
    from math import radians, cos, sin, asin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return int(c * r)
    
def get_slots(words):
    #Minimize mistake for the answer or question by pre-process the country name and time
    slots = {}
    rest_words = list(words)
    country_name = ['宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣', '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市', '基隆市', '新竹縣', '新竹市', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '嘉義市', '屏東縣']
    country_nickname = ['宜蘭', '花蓮', '臺東', '台東', '台東縣', '澎湖', '金門', '連江', '臺北', '台北', '台北市', '新北', '桃園', '臺中', '台中', '台中市', '臺南', '台南', '台南市', '高雄', '基隆', '新竹', '苗栗', '彰化', '南投', '雲林', '嘉義', '屏東', '馬祖']
    mapping = {'台東縣': '臺東縣', '基隆': '基隆市', '臺南': '臺南市', '新北': '新北市', '台北市': '臺北市', '台中': '臺中市', '馬祖': '連江', '台中市': '臺中市', '台南市': '臺南市', '台北': '臺北市', '金門': '金門縣', '澎湖': '澎湖縣', '台東': '臺東縣', '桃園': '桃園市', '苗栗': '苗栗縣', '臺東': '臺東縣', '臺北': '臺北市', '臺中': '臺中市', '連江': '連江縣', '屏東': '屏東縣', '彰化': '彰化縣', '新竹': '新竹市', '花蓮': '花蓮縣', '高雄': '高雄市', '嘉義': '嘉義市', '南投': '南投縣', '宜蘭': '宜蘭縣', '台南': '臺南市', '雲林': '雲林縣'}
    time_name = ['今天','現在','明天']
    for word in words:
        if word in country_name:
            slots["space"] = word
            rest_words.remove(word)
        if word in country_nickname:
            slots["space"] = mapping[word]
            rest_words.remove(word)
    for word in words:
        if word in time_name:
            if word in ['今天','現在']:
                slots['time'] = 'now'
                rest_words.remove(word)
            elif word in ['明天']:
                slots['time'] = 'next'
                rest_words.remove(word)
    return slots, rest_words