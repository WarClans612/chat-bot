# -*- coding: utf-8 -*-
from sensor_fetch import weather
from sensor_fetch import pm25
from sensor_fetch import uvi
from sensor_fetch import rainfall

#Bound declared in global variable for checking
rain_bound = [20]
temperature_bound = [20,30]
air_quality_bound = [10,15,25,35]
uvi_bound = [6,8,11]
rainfall_bound = [80,200,350,500]

############################################################################

def get_weather(slots):
    if "space" not in slots:
        slots["space"] = "新竹市"
    if "time" not in slots:
        slots["time"] = "now"
    weather_info = weather.get(name = slots["space"], time = slots["time"])
    if weather_info is None:
        return None
    temperature = float(weather_info["temperature"])
    rainfull_prob = int(weather_info["rainfull_prob"])
    return temperature, rainfull_prob
    
def get_air_quality(slots):
    if slots.get("SiteName"):
        air_quality = pm25.get(name = slots["SiteName"])
    else:
        air_quality = pm25.get(name = slots["space"])
    if air_quality is None:
        return None
    return float(air_quality)
    
def get_uvi(slots):
    if slots.get("SiteName"):
        uvi_value = uvi.get(name = slots["SiteName"])
    else:
        uvi_value = uvi.get(name = slots["space"])
    if uvi_value is None:
        return None
    return float(uvi_value)
    
def get_rainfall(slots):
    if slots.get("space"):
        rainfall1hr = rainfall.get(name = slots["space"], hours = 1)
        rainfall24hr = rainfall.get(name = slots["space"], hours = 24)
    if rainfall1hr is None or rainfall24hr is None:
        return None
    return rainfall1hr, rainfall24hr
    
############################################################################

def get_weather_answer_code(slots):
    value = get_weather(slots)
    if value is None:
        return 0, 0, 0
    temperature, rainfull_prob = value
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

def get_rain_answer_code(slots):
    value = get_weather(slots)
    if value is None:
        return 0, 0, 0
    temperature, rainfull_prob = value
    if rainfull_prob < rain_bound[0]:
        answer_code = 1
    else:
        answer_code = 2
    return temperature, rainfull_prob, answer_code

def get_pm25_answer_code(slots):
    value = get_air_quality(slots)
    if value is None:
        return 0, 0
    air_quality = value
    if air_quality < air_quality_bound[0]:
        answer_code = 1
    elif air_quality < air_quality_bound[1]:
        answer_code = 2
    elif air_quality < air_quality_bound[2]:
        answer_code = 3
    else:
        answer_code = 4
    return air_quality, answer_code

def get_goout_answer_code(slots):
    value1 = get_air_quality(slots)
    value2 = get_weather(slots)
    value3 = get_uvi(slots)
    if value1 is None or value2 is None or value3 is None:
        return 0, 0, 0, 0, 0
    air_quality = value1
    temperature, rainfull_prob = value2
    uvi = value3
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
    return air_quality, temperature, rainfull_prob, uvi, answer_code

def get_uvi_answer_code(slots):
    value = get_uvi(slots)
    if value is None:
        return 0, 0
    uvi = value
    if uvi < uvi_bound[0]:
        answer_code = 1
    elif uvi < uvi_bound[1]:
        answer_code = 2
    elif uvi < uvi_bound[2]:
        answer_code = 3
    else:
        answer_code = 4
    return uvi, answer_code
    
def get_rainfall_answer_code(slots):
    value = get_rainfall(slots)
    if value is None:
        return 0, 0, 0
    rainfall1hr, rainfall24hr = value
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
    return rainfall1hr, rainfall24hr, answer_code