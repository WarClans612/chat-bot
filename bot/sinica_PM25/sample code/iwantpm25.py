# -*- coding: utf-8 -*-
"""
Created on Fri May  5 17:35:35 2017

@author: SensorTeam
"""

import json 
import ast
import csv
import sys 
import pandas as pd
import data_archive
import os

#### User parameter ####
year = '2017'
month = '02'
day = '09'

time = "07:00:00"

location = "Hsinchu"


longi = 24.805619
lati = 120.972075

#########

def get_PM25_inlocation(location, json_read):
    #coordinates = []
    #coordinates.append(longi)
    #coordinates.append(lati)
    for index in range(len(json_read)):
        if json_read[index]['SiteEngName'] == location:  
            if json_read[index]['time'] == time:
                print (time+ " "+ str(longi)+" "+str(lati))
                print (json_read[index]['SiteEngName'])
                print ("PM25 = "+ str(json_read[index]['PM2_5']) )
                return ( json_read[index]['PM2_5'] )
    return "Can not get PM25"

def find_PM25():
    filename = os.path.join(os.getcwd(),"data","pm25_epa_"+year+month+day+'.txt')
    
    try:
        with open(filename , 'r') as files:
            data = files.read()
    except:
        data_archive.start_download_data(year,month,day)
        with open(filename , 'r') as files:
            data = files.read()
    
        
    data = data.replace("b'","")
    data = data.replace("'", "")
    data = data.replace("\\","_")
    
    json_read = json.loads(data)

    return get_PM25_inlocation(location, json_read) 
    
    


if __name__ == '__main__':
    
    ### use this to get PM25 value
    PM25 = find_PM25()
    print(PM25)
    



        

        
        


        
