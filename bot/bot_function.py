# -*- coding: utf-8 -*-
"""
{"WEATHER": "天氣" , "RAIN": "降雨" , "PM25": "PM2.5" ,"GOOUT": "戶外資訊" ,"UVI": "紫外線指數"}
"""
import jieba.analyse
from pymongo import MongoClient
from bot.util import BotUtil

default_message = "找不到符合的答案"

def segment(question):
    '''
        This function return the question in segmented list
        Possible output ['今天' ,'臺南', '溫度']
    '''
    topK = 20
    withWeight = False
    allowPOS = ()
    return jieba.analyse.extract_tags(question, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
    
def get_answer(question_num, slots):
    '''
        This function return answer sentence from the given question_num
    '''
    client = BotUtil()
    db = client._bot_db
    
    #Try to find the wanted entry
    collect = db['question_table']
    question_table = collect.find_one({'question_num':question_num})
    #If no entry is found, return default message
    if question_table is None:
        return default_message

    handle_code = question_table['handle_code']
    type = question_table['type']
    
    #Check answer type and return as needed
    #Sky condition
    if type == "i":
        HL = question_table['HL_code']
        answer = client.i_handler(question_num, handle_code, HL, slots)
    #General QA
    elif type == "general":
        answer_table = db["answer_table"].find_one({'question_num':question_num})
        answer = answer_table['answer']
    #Sensor Data Related QA
    else:
        answer = client.sensor_handler("normal", handle_code, slots)
    return answer
    
def get_location_sQA_answer(question_num,slots,location):
    client = BotUtil()
    db = client._bot_db
    
    collect = db['question_table']
    handle_code = collect.find_one({'question_num':question_num})['handle_code']
    
    if handle_code in ["PM25","UVI"]:
        slots["SiteName"] = client.nearest_station(handle_code, location)
        slots["space"] = "您最接近{station}測站,".format(station=slots["SiteName"])

    answer = client.sensor_handler(handle_code,slots)
    return answer
    
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