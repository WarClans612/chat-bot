# coding: utf-8
#!/usr/bin/env python

import json 
import ast
import csv
import sys 
import pandas as pd



#filename = 'F:/DATA/Data-Archive/sample code/pm25_airbox_0205.txt'
filename = 'C:\\Users\\SensorTeam\\Desktop\\Da_workspace\\sinica\\sample code\\pm25_epa_0209.txt'

with open(filename , 'r') as files:
    data = files.read()

data = data.replace("'", "")
#data_replace_chinese = data.replace("\\", "") #just for airbox


data_dic= ast.literal_eval(data) #just for epa (str to dic)
#data_json = json.loads(data_replace_chinese) #just for airbox


# utf-8 problem
#reload(sys)                         
#sys.setdefaultencoding('utf-8')


# full keyerror with NA
def get_node(name, node):
    try:
        val = node[name]
    except KeyError:
        val = 'NA'
    return val

##----------------------epa data--------------------------------------
f = csv.writer(open("pm25_epa_0209.csv", "wb+"))

## Write CSV Header
f.writerow(["ver_format","fmt_opt","app","date","time","Status","PSI","CO","SiteEngName","PM10","NO","SiteName","FPMI","WindDirec","PM2_5","PublishTime","County","WindSpeed","SO2","NOx","SiteType",            "O3","NO2","type","coordinates"])

for x in data_dic:
    f.writerow([get_node("ver_format", x),get_node("fmt_opt", x),get_node("app", x),get_node("date", x),get_node("time", x),get_node("Status", x), get_node('PSI', x), get_node("CO", x),                 get_node("SiteEngName", x),get_node("PM10", x),get_node("NO", x),get_node("SiteName", x),                 get_node("FPMI", x),get_node("WindDirec", x),get_node("PM2_5", x),get_node("PublishTime", x),                 get_node("County", x),get_node("WindSpeed", x),get_node("SO2", x),get_node("NOx", x),                 get_node("SiteType", x),get_node("O3", x),get_node("NO2", x),                 x["loc"]["type"],x["loc"]["coordinates"]])
    ##-------------end----------------------


##----------------------airbox data--------------------------------------
#f = csv.writer(open("pm25_airbox_0205.csv", "wb+"))

## Write CSV Header           //remove device  & SiteName 
#f.writerow(["ver_format","fmt_opt","app","ver_app","device_id","tick","s_0","s_1","s_2","s_3","s_d0","s_d1","s_d2","s_t0","s_h0","gps_fix","gps_num","gps_alt","date","time","type","coordinates"])

#for x in data_json:
    #f.writerow([get_node("ver_format", x),get_node("fmt_opt", x),get_node("app", x),get_node("ver_app", x),get_node("device_id", x),get_node("tick", x), get_node("s_0", x),get_node("s_1", x),get_node("s_2", x),get_node("s_3", x),get_node("s_d0", x),get_node("s_d1", x),get_node("s_d2", x),get_node("s_t0", x),get_node("s_h0", x), get_node("gps_fix", x),get_node("gps_num", x),get_node("gps_alt", x),get_node("date", x),get_node("time", x),x["loc"]["type"],x["loc"]["coordinates"]])
    ##-----------end----------------------------------------------------

    

#(optional) csv to xlsx
#df = pd.read_csv('pm25_airbox_0206.csv')
#df.to_excel('pm25_airbox_0206.xlsx', encoding='utf-8')


