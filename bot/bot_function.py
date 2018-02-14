#!/usr/bin/python

import jieba
import jieba.analyse
from pymongo import MongoClient
import sys
import bot_config
import re
#import WeatherAPI.weather as weather
#import my_pm25 as pm25
from sensor_fetch import get_pm25 as pm25
from sensor_fetch import get_weather as weather
from sensor_fetch import get_uvi as UVI
from sensor_fetch import get_rainfall as RAINF
from sensor_fetch import get_most
from sensor_fetch import get_where
from datetime import datetime #datetime.datetime
import urllib.request
import urllib.parse

topK = 20
withWeight = False
allowPOS = ()
default_message = "找不到符合的答案"

def open_qa_file(filename):
    question_set = []
    answer_set = []
    i = 0
    with open(filename, 'r', encoding='utf8') as fp:
        for line in fp:
            text = line.strip()
            if i % 2 == 0:
                question_set.append(text)
            else:
                answer_set.append(text)
            i += 1
    return question_set, answer_set

def init_jieba(stop_words_filename, idf_filename, question_set):
    jieba.analyse.set_stop_words(stop_words_filename)
    jieba.analyse.set_idf_path(idf_filename)

    keyword_set = [] 
    num_of_keyword = []
    keywords = []

    for question in question_set:
        words = jieba.analyse.extract_tags(question, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
        keyword_set.append(words)
        num_of_keyword.append(len(words))
        keywords.extend(words)

    return keywords, keyword_set, num_of_keyword

def qa_questoining(source, question_file):
    questions = []
    if source=='input':
        text = input("==>")
        questions.append(text)
    elif source=='file':
        with open(question_file, 'r', encoding='utf8') as fp:
            for line in fp:
                text = line.strip()
                questions.append(text)
    else:
        print('error in qa_questoining : no such source!')
    return questions
    
def qa_answering(sentence, answer_db, keyword_set_db):
    scores = {}
    words = jieba.analyse.extract_tags(sentence, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
    match_keywords = []
    for word in words:
        for i in range(len(keyword_set_db)):
            if word in keyword_set_db[i]:
                match_keywords.append(word)
                found = scores.get(i)
                if found is None:
                    found = 0
                found += 1.0 / len(keyword_set_db[i])
                scores[i] = found
    print ('keywords in questioning: '+'/'.join(words))
    print ('keywords matched: '+'/'.join(match_keywords))
    print ()
    if len(scores) == 0:
        return default_message
    else:
        index = max(scores, key=scores.get)
        print (str(scores.get(index))+'%matched')
        return answer_db[index]
        
        
def segment(question):
    url = bot_config.segment_api_url
    target_url = urllib.request.Request(url+ urllib.parse.quote(question.strip(), safe=''))
    with urllib.request.urlopen(target_url) as res:
        data_list = res.read().decode('utf-8')
    words = data_list.split("/")
    return words

def get_weather_answer_code(slots):
    rain_bound = [20]
    temperature_bound = [20,30]
    temperature, rainfull_prob = get_weather(slots)
    if rainfull_prob < rain_bound[0]:
        if temperature < temperature_bound[0]:
            answer_code = 1
        elif temperature < temperature_bound[1]:
            answer_code = 2
        else:
            answer_code = 3
    else:
        if temperature < temperature_bound[0]:
            answer_code = 4
        elif temperature < temperature_bound[1]:
            answer_code = 5
        else:
            answer_code = 6
    return temperature, rainfull_prob, answer_code

def get_uvi_answer_code(slots):
    uvi_bound = [6,8,11]
    uvi = get_uvi(slots)
    if uvi < uvi_bound[0]:
        answer_code = 1
    elif uvi < uvi_bound[1]:
        answer_code = 2
    elif uvi < uvi_bound[2]:
        answer_code = 3
    else:
        answer_code = 4
    return uvi, answer_code

def sensor_handler(handle_code,slots):
    rain_bound = [20]
    temperature_bound = [20,30]
    air_quality_bound = [10,15,25,35]
    uvi_bound = [6,8,11]
    rainfall_bound = [80,200,350,500]
    temperature = 0
    rainfull_prob = 0
    air_quality = 0
    uvi = 0
    rainfall1hr = 0
    rainfall24hr = 0
    if handle_code == "WEATHER" :
        temperature, rainfull_prob, answer_code = get_weather_answer_code(slots)
    elif handle_code == "RAIN":
        temperature, rainfull_prob = get_weather(slots)
        if rainfull_prob < rain_bound[0]:
            answer_code = 1
        else:
            answer_code = 2
    elif handle_code == "PM25":
        air_quality = get_air_quality(slots)
        if air_quality < air_quality_bound[0]:
            answer_code = 1
        elif air_quality < air_quality_bound[1]:
            answer_code = 2
        elif air_quality < air_quality_bound[2]:
            answer_code = 3
        else:
            answer_code = 4
    elif handle_code == "GOOUT":
        air_quality = get_air_quality(slots)
        temperature, rainfull_prob = get_weather(slots)
        uvi = get_uvi(slots)
        if uvi < uvi_bound[1]:
            if air_quality < air_quality_bound[1]:
                if rainfull_prob < rain_bound[0]:
                    if temperature < temperature_bound[0]:
                        answer_code = 1
                    elif temperature < temperature_bound[1]:
                        answer_code = 2
                    else:
                        answer_code = 3
                else:
                    if temperature < temperature_bound[0]:
                        answer_code = 4
                    elif temperature < temperature_bound[1]:
                        answer_code = 5
                    else:
                        answer_code = 6
            else:
                if rainfull_prob < rain_bound[0]:
                    if temperature < temperature_bound[0]:
                        answer_code = 7
                    elif temperature < temperature_bound[1]:
                        answer_code = 8
                    else:
                        answer_code = 9
                else:
                    if temperature < temperature_bound[0]:
                        answer_code = 10
                    elif temperature < temperature_bound[1]:
                        answer_code = 11
                    else:
                        answer_code = 12
        else:
            if air_quality < air_quality_bound[1]:
                if rainfull_prob < rain_bound[0]:
                    if temperature < temperature_bound[0]:
                        answer_code = 13
                    elif temperature < temperature_bound[1]:
                        answer_code = 14
                    else:
                        answer_code = 15
                else:
                    if temperature < temperature_bound[0]:
                        answer_code = 16
                    elif temperature < temperature_bound[1]:
                        answer_code = 17
                    else:
                        answer_code = 18
            else:
                if rainfull_prob < rain_bound[0]:
                    if temperature < temperature_bound[0]:
                        answer_code = 19
                    elif temperature < temperature_bound[1]:
                        answer_code = 20
                    else:
                        answer_code = 21
                else:
                    if temperature < temperature_bound[0]:
                        answer_code = 22
                    elif temperature < temperature_bound[1]:
                        answer_code = 23
                    else:
                        answer_code = 24
    elif handle_code == "UVI":
        uvi, answer_code = get_uvi_answer_code(slots)
    elif handle_code == "RAINFALL":
        rainfall1hr, rainfall24hr = get_rainfall(slots)
        if rainfall24hr < rainfall_bound[0] and rainfall1hr < 40:
            answer_code = 1
        elif rainfall24hr < rainfall_bound[1]:
            answer_code = 2
        elif rainfall24hr < rainfall_bound[2]:
            answer_code = 3
        elif rainfall24hr < rainfall_bound[3]:
            answer_code = 4
        else:
            answer_code = 5
    else: 
        print("[err: no such handle_code -- ",handle_code," ]")
        
    ###connect to DB:"bot"
    db_url = bot_config.db_url 
    db_name = bot_config.db_name
    client = MongoClient(db_url)
    db = client[db_name]
    A_template = db.handle_table.find_one({'handle_code':handle_code, 'answer_code':answer_code })['A_template']
    answer = A_template 
    replace_mapping = {"#temperature#" : temperature , "#rainfull_prob#" : rainfull_prob , "#pm25#" : air_quality , "#uvi#" : uvi, "#rainfall1hr#" : rainfall1hr , "#rainfall24hr#" : rainfall24hr}
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
    return answer

def sensor_handler_for_subscription(handle_code,slots):
    rain_bound = [20]
    temperature_bound = [20,30]
    air_quality_bound = [10,15,25,35]
    uvi_bound = [6,8,11]
    temperature = 0
    rainfull_prob = 0
    air_quality = 0
    uvi = 0
    if handle_code == "WEATHER" :
        temperature, rainfull_prob, answer_code = get_weather_answer_code(slots)
    elif handle_code == "RAIN":
        temperature, rainfull_prob = get_weather(slots)
        if rainfull_prob < rain_bound[0]:
            answer_code = 1
        else:
            answer_code = 2
    elif handle_code == "PM25":
        air_quality = get_air_quality(slots)
        if air_quality < air_quality_bound[0]:
            answer_code = 1
        elif air_quality < air_quality_bound[1]:
            answer_code = 2
        elif air_quality < air_quality_bound[2]:
            answer_code = 3
        else:
            answer_code = 4
    elif handle_code == "GOOUT":
        air_quality = get_air_quality(slots)
        temperature, rainfull_prob = get_weather(slots)
        uvi = get_uvi(slots)
        if uvi < uvi_bound[1]:
            if air_quality < air_quality_bound[1]:
                if rainfull_prob < rain_bound[0]:
                    if temperature < temperature_bound[0]:
                        answer_code = 1
                    elif temperature < temperature_bound[1]:
                        answer_code = 2
                    else:
                        answer_code = 3
                else:
                    if temperature < temperature_bound[0]:
                        answer_code = 4
                    elif temperature < temperature_bound[1]:
                        answer_code = 5
                    else:
                        answer_code = 6
            else:
                if rainfull_prob < rain_bound[0]:
                    if temperature < temperature_bound[0]:
                        answer_code = 7
                    elif temperature < temperature_bound[1]:
                        answer_code = 8
                    else:
                        answer_code = 9
                else:
                    if temperature < temperature_bound[0]:
                        answer_code = 10
                    elif temperature < temperature_bound[1]:
                        answer_code = 11
                    else:
                        answer_code = 12
        else:
            if air_quality < air_quality_bound[1]:
                if rainfull_prob < rain_bound[0]:
                    if temperature < temperature_bound[0]:
                        answer_code = 13
                    elif temperature < temperature_bound[1]:
                        answer_code = 14
                    else:
                        answer_code = 15
                else:
                    if temperature < temperature_bound[0]:
                        answer_code = 16
                    elif temperature < temperature_bound[1]:
                        answer_code = 17
                    else:
                        answer_code = 18
            else:
                if rainfull_prob < rain_bound[0]:
                    if temperature < temperature_bound[0]:
                        answer_code = 19
                    elif temperature < temperature_bound[1]:
                        answer_code = 20
                    else:
                        answer_code = 21
                else:
                    if temperature < temperature_bound[0]:
                        answer_code = 22
                    elif temperature < temperature_bound[1]:
                        answer_code = 23
                    else:
                        answer_code = 24
    elif handle_code == "UVI":
        uvi, answer_code = get_uvi_answer_code(slots)
    else: 
        print("[err: no such handle_code -- ",handle_code," ]")
        
    ###connect to DB:"bot"
    db_url = bot_config.db_url 
    db_name = bot_config.db_name
    client = MongoClient(db_url)
    db = client[db_name]
    A_template = db.handle_table.find_one({'handle_code':handle_code, 'answer_code':answer_code })['A_template']
    answer = A_template
    replace_mapping = {"#temperature#" : temperature , "#rainfull_prob#" : rainfull_prob , "#pm25#" : air_quality , "#uvi#" : uvi}
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
    
    if handle_code == "RAIN" and answer_code<=1:
        answer = None
    elif handle_code == "PM25" and answer_code <= 2 :
        answer = None
    elif handle_code == "UVI" and answer_code <= 2 :
        answer = None

    return answer

def i_handler(question_num,handle_code,HL,slots):
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
            result, wx = get_where.if_rainbow(slots)
            if result == True:
                answer = slots["space"]+time+"天氣"+wx+" 有機會看到彩虹喔!"
            else:
                answer = slots["space"]+time+"天氣"+wx+" 不太有機會看到彩虹"
            return answer
        else:
            county_list = get_where.get_where_rainbow(slots)
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
            result, wx = get_where.if_sunrise(slots)
            if result == True:
                answer = slots["space"]+"明天清晨天氣"+wx+" 有機會看到日出喔!"
            else:
                answer = slots["space"]+"明天清晨天氣"+wx+" 不太有機會看到日出"
        else:
            recommend_list, county_list = get_where.get_where_sunrise()
            if len(recommend_list) != 0:
                answer = "推薦可以到"+"、".join(recommend_list)+"欣賞日出,明天清晨天氣不錯"
            elif len(county_list) !=0:
                answer = "明天清晨天氣較佳有機會欣賞日出的縣市如下:"+"、".join(county_list)+" 祝您有個愉快的一天"
            else:
                answer = "明天清晨全臺天氣都不佳，可能比較沒有機會看到日出喔"
        return answer
    else:
        values,space = get_most.get_most(handle_code,HL)
        
        ###connect to DB:"bot"
        db_url = bot_config.db_url 
        db_name = bot_config.db_name
        client = MongoClient(db_url)
        db = client[db_name]
        answer = db.answer_table.find_one({'question_num':question_num})['answer']
        
        temperature = values["temperature"]
        air_quality = values["pm25"]
        uvi = values["uvi"]
        rainfall24hr = values["rainfall24hr"]
        
        replace_mapping = {"#temperature#" : temperature , "#pm25#" : air_quality , "#uvi#" : uvi, "#rainfall24hr#" : rainfall24hr}
        for pattern in replace_mapping :
            if re.search(pattern, answer) != None:
                answer = re.sub(pattern, str(replace_mapping[pattern]), answer)
        answer = re.sub("#space#", space, answer)
        return answer
    
def get_answer(question_num,slots):
    ###connect to DB:"bot"
    db_url = bot_config.db_url 
    db_name = bot_config.db_name
    client = MongoClient(db_url)
    db = client[db_name]
    handle_code = db.question_table.find_one({'question_num':question_num})['handle_code']
    type = db.question_table.find_one({'question_num':question_num})['type']
    
    if type == "i":
        HL = db.question_table.find_one({'question_num':question_num})['HL_code']
        answer = i_handler(question_num,handle_code,HL,slots)
    elif type == "general" : #general QA
        answer = db.answer_table.find_one({'question_num':question_num})['answer']
    else : #sensor related QA
        answer = sensor_handler(handle_code,slots)
    return answer
    
def get_location_sQA_answer(question_num,slots,location):
    ###connect to DB:"bot"
    db_url = bot_config.db_url 
    db_name = bot_config.db_name
    client = MongoClient(db_url)
    db = client[db_name]
    handle_code = db.question_table.find_one({'question_num':question_num})['handle_code']
    

    if handle_code == "PM25" or handle_code =="UVI":
        slots["SiteName"] = nearest_station(handle_code, location)
        slots["space"] = "您最接近"+slots["SiteName"]+"測站,"

    answer = sensor_handler(handle_code,slots)
    
    
    #mapping = {"WEATHER": "天氣" , "RAIN": "降雨" , "PM25": "PM2.5" ,"GOOUT": "戶外資訊" ,"UVI": "紫外線指數"}
    
    return answer

def nearest_station(handle_code, location):
    user_lon = location['long']
    user_lat = location['lat']
    
    ###connect to DB:"bot"
    db_url = bot_config.db_url 
    db_name = bot_config.db_name
    client = MongoClient(db_url)
    db = client[db_name]
    
    if handle_code == "PM25":
        station_list = db.pm25_station_data.find()
    else : # "UVI"
        station_list = db.uvi_station_data.find()
    
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

def get_weather(slots):
    if "space" not in slots:
        slots["space"] = "新竹市"
    if "time" not in slots:
        slots["time"] = "now"
    weather_info = weather.get_weather(Location_name = slots["space"], time = slots["time"])
    temperature = float(weather_info["temperature"])
    rainfull_prob = int(weather_info["rainfull_prob"])
    return temperature, rainfull_prob
    
def get_air_quality(slots):
    #air_quality = 18
    if slots.get("SiteName"):
        air_quality = pm25.get_pm25_station(slots["SiteName"])
    else:
        air_quality = pm25.get_pm25(slots["space"])
    return float(air_quality)
    
def get_uvi(slots):
    if slots.get("SiteName"):
        uvi = UVI.get_uvi_station(slots["SiteName"])
    else:
        uvi = UVI.get_uvi(slots["space"])
    return float(uvi)
    
def get_rainfall(slots):
    if slots.get("space"):
        rainfall1hr, rainfall24hr = RAINF.get_rainfall(slots["space"])
    return rainfall1hr, rainfall24hr
    
def get_slots(words):
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
    
if __name__ == '__main__':
    ### Init QA from file
    filename = '課程抵免QA.txt'
    question_set, answer_set = open_qa_file(filename)

    ### Initialize jieba
    stop_words_filename = 'extra_dict/stop_words.txt'
    idf_filename = 'extra_dict/idf.txt.big'
    keywords, keyword_set, num_of_keyword = init_jieba(stop_words_filename, idf_filename, question_set)

    ### Testing the module
    #questions = ['我想問課程抵免問題?', '我可以抵免計算機網路概論嗎?', '我想要問要幾分才可以抵免?']
    #source from file
    """
    source = 'file'
    question_file = '課程抵免_questions.txt'
    questions = qa_questoining(source, question_file)
    for q in questions:
        a = qa_answering(q, answer_set, keyword_set)
        print(q)
        print(a)
        print()
    """
    #source from input
    source = 'input'
    question_file = ''
    while 1==1:
        questions = qa_questoining(source, question_file)
        q = questions[0]
        a = qa_answering(q, answer_set, keyword_set)
        print('Q: '+q)
        print('A: '+a)
        print()
    
    """
    #source from training set
    questions = question_set
    for q in questions:
        a = qa_answering(q, answer_set, keyword_set)
        print(q)
        print(a)
        print()
    """
