import urllib.request
import json
from datetime import datetime
from pymongo import MongoClient
from sensor_config import *

def grab_data():
    urll = 'http://opendata.epa.gov.tw/ws/Data/RainTenMin/?format=json'
    fp = urllib.request.urlopen(urll)
    data_list = json.loads(fp.read().decode('utf-8'))
    fp.close()
    
    return data_list

def save_rainfall():
    county_list = []
    data_list = grab_data()
    new_data_list = []
    for i in data_list:
        county = i['County']   
        if county not in county_list:
            county_list.append(county)
            data = {}  
            time = datetime.strptime(i['PublishTime'], "%Y-%m-%d %H:%M:%S")
            data['County'] = county
            data['rainfall1hr'] = float(i['Rainfall1hr'])
            data['rainfall24hr'] = float(i['Rainfall24hr'])
            data['PublishTime'] = time
            print(data)
            new_data_list.append(data)
    
    db_url = "{host}:27017".format(host=mongo_host)
    db_name = 'bot'
    client = MongoClient(db_url,  27017)
    db = client[ 'bot']
    collect = db['rainfall_data']
    collect.insert(new_data_list)
    
    return time
    
if __name__ == "__main__":
    save_rainfall()
