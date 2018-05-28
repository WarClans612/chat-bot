#!/usr/bin/python
import re
from pymongo import MongoClient
from bot import bot_config
from bot.bot_answer_code import *
from sensor_fetch import sensor_highest_value
from sensor_fetch import sky

default_message = "找不到符合的答案"

def _connect_to_database():
    db_url = bot_config.db_url 
    db_name = bot_config.db_name
    client = MongoClient(db_url)
    db = client[db_name]
    return db

class BotUtil:
    _bot_db = _connect_to_database()
    
    def sensor_handler(self, types, handle_code, slots):
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
            return '資料 Sensor 不反應'
    
        collect = self._bot_db['handle_table']
        A_template = collect.find_one({'handle_code':handle_code, 'answer_code':answer_code })['A_template']
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
            if handle_code == "RAIN" and answer_code <= 1:
                answer = None
            elif handle_code == "PM25" and answer_code <= 2 :
                answer = None
            elif handle_code == "UVI" and answer_code <= 2 :
                answer = None
        
        return answer
        
    def i_handler(self, question_num,handle_code,HL,slots):
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
            
            collect = self._bot_db['answer_table']
            answer = collect.find_one({'question_num':question_num})['answer']
            
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
            
    def nearest_station(self, handle_code, location):
        user_lon = location['long']
        user_lat = location['lat']
        
        if handle_code == "PM25":
            station_list = self._bot_db['pm25_station_data'].find()
        else : # "UVI"
            station_list = self._bot_db['uvi_station_data'].find()
        
        first = station_list[0]
        SiteName = first["SiteName"]
        min_D = self.haversine(user_lon, user_lat, first["Lon"], first["Lat"])
        for station in station_list:
            D = self.haversine(user_lon, user_lat, station["Lon"], station["Lat"])
            if D < min_D:
                min_D = D
                SiteName = station["SiteName"]
        return SiteName
        
    def haversine(self, lon1, lat1, lon2, lat2):
        from math import radians, cos, sin, asin, sqrt
    
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371
        return int(c * r)
