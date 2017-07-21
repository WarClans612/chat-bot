#!/usr/bin/env python
# Objctive: This program will do the following:
#     * retrieve the data from Cassandra

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

import json
import csv
import sys
import os 

data =[]
# set the default program encoding to 'utf-8'
#reload( sys )
#sys.setdefaultencoding('utf-8')
from datetime import datetime
from datetime import timedelta
import time

# Program Configuration ----------------------------
import config
Cassandra_SERVER = config.Cassandra_SERVER
Cassandra_USER = config.Cassandra_USER
Cassandra_PASS = config.Cassandra_PASS
Cassandra_CONSISTLEVEL = config.Cassandra_CONSISTLEVEL
Cassandra_FETCH_SIZE = config.Cassandra_FETCH_SIZE
Cassandra_TIMEOUT = config.Cassandra_TIMEOUT
Cassandra_ARCHIVE = config.Cassandra_ARCHIVE
LIST_SOURCES = config.LIST_SOURCES
# ---------------------------- Program Configuration

# Database Connection ------------------------------
# connect to Cassandra
auth_provider = PlainTextAuthProvider( username = Cassandra_USER, password = Cassandra_PASS )
# bypass the ssl check hostname procedure, which enables the program to connect to cassandra through local IP
ssl_options = {'check_hostname': False}
casscluster = Cluster( [ Cassandra_SERVER ], auth_provider = auth_provider, ssl_options = ssl_options )
casssession = casscluster.connect( Cassandra_ARCHIVE )
casssession.default_timeout = 60
# ------------------------------ Database Connection

##################################################
# the following parameters should be modified:
YEAR = '2017'
MONTH = '03'
DAY = '9'
##################################################


def start_download_data(year, month, day):
    # start to archive the data
    for SOURCE in LIST_SOURCES:
    	# the Cassandra query command
    	# ------------------------------
    	# notes that:
    	#  1. it is require to provide the source name!
    	#  2. DO NOT REMOVE THE "ALLOW FILTERING" OPTION!
    	# ------------------------------
    	# query for 1 month's data:
    	Command = "SELECT data FROM " + Cassandra_ARCHIVE +  ".all WHERE source='" + SOURCE + "' and year=" + str( int(year) ) + " and month=" + str( int( month ) )  + " and day=" + str( int( day ) ) + " ALLOW FILTERING;"
    	# query for a date (ex. 2017-02-01):
    	# Command = "SELECT data FROM " + Cassandra_ARCHIVE +  ".all WHERE source='" + SOURCE + "' and year=" + str( YEAR ) + " and month=" + str( int( MONTH ) ) + " and day=" + str( int( DAY ) ) + " ALLOW FILTERING;"
    	statement = SimpleStatement( Command, consistency_level = Cassandra_CONSISTLEVEL, fetch_size = Cassandra_FETCH_SIZE )
    
    	try:
    		# start archiving the data to the local database here!
    		# ############################################################
    		for result in casssession.execute( statement, timeout = Cassandra_TIMEOUT ):
    			record = str( result.data ).replace( '\n', '' ).replace( '\r', '' )#.encode( 'utf-8' )
    			print( record )
    			
    			##### your code here... #####
    			
    			data.append(record)
    
    		#print type(data)
    
    		#thefile = open('pm25data0205.txt', 'w')
    		#for item in data:
    			#thefile.write("%s\n" % item)
    
    		with open(os.path.join(os.getcwd(),"data","pm25_epa_"+year+month+day+'.txt'), "w" ) as output:
    			output.write(str(data))
    
      
    		#f = csv.writer(open("pm25data0205.csv","w"))
    		#for x in data :
    			#f.writerow([x["ver_format"],x["fmt_opt"],x["app"],x["ver_app"],x["device_id"],x["tick"],x["device"],x["s_0"],x["s_1"],x["s_2"],\
    				#x["s_3"],x["s_d0"],x["s_d1"],x["s_d2"],x["s_t0"],x["s_h0"],x["gps_fix"],x["gps_num"],x["gps_alt"],x["date"],\
    				#x["time"],x["SiteName"],x["loc"]["type"],x["loc"]["coordinates"]])
    
    		#epa: 
    		#[x["ver_format"],x["fmt_opt"],x["app"],x["date"],x["time"],x["Status"],x["PSI"],x["CO"],x["SiteEngName"],x["PM10"],x["NO"],x["SiteName"],
    				#x["FPMI"],x["WindDirec"],x["PM2_5"],x["PublishTime"],x["County"],x["WindSpeed"],x["SO2"],x["NOx"],x["SiteType"],
    				#x["O3"]x["NO2"],x["loc"]["type"],x["loc"]["coordinates"]]
    
    
    			 
    
    		# ############################################################
    	except Exception as ex:
    		print( "[ERROR] (" + str( ex ) + ") Cassandra Query Error for the command: " + str( Command ) )
    		print( "[ERROR] Probably no data available for this source!" )
    		continue
    
    # close the database connections
    casscluster.shutdown()
	
if __name__ == '__main__':
	year = '2017'
	month = '06'
	day = '3'
	start_download_data(year, month, day)
	
	