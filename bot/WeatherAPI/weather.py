# encoding=utf-8
from pprint import pprint
import urllib.request
import urllib.parse
import json

def parse_json_data(pure_data):
    location = pure_data['records']['location']
    Location_list = dict()
    for L in location:
        Location_list[L['locationName']] = dict()
        for element in L['weatherElement']:
            for E in element['time']:
                if( E['startTime'] not in Location_list[L['locationName']] ):
                    Location_list[L['locationName']][E['startTime']] = dict()
                    Location_list[L['locationName']][E['startTime']]['endTime'] = E['endTime']
                Location_list[L['locationName']][E['startTime']][element['elementName']] = E['parameter']['parameterName']
    return Location_list

def grab_data():
    Data_set = input("請輸入資料集編號: ")
    Location_name = input("請輸入地點(預設全選): ")

#connect to cwb api
    urll = 'http://opendata.cwb.gov.tw/api/v1/rest/datastore/'+Data_set+'?'
    Location_name = Location_name.strip()
    if Location_name:
        urll = urll+'locationName='
        target_url = urllib.request.Request(urll+ urllib.parse.quote(Location_name, safe='')+'&sort=time')
    else:
        target_url = urllib.request.Request(urll+ urllib.parse.quote(Location_name, safe='')+'sort=time')

    with open("token.txt","r") as token_file:
        token = token_file.readline().rstrip('\n')
    target_url.add_header( 'Authorization' , token)
    fp = urllib.request.urlopen(target_url)
    pure_data = json.loads(fp.read().decode('utf-8'))
    fp.close()

    with open("output.json","w") as file:
        pprint(pure_data,file)

    data_list = parse_json_data(pure_data)

    with open("output.dat","w") as file:
        pprint(data_list,file)

    return data_list
    
grab_data()

