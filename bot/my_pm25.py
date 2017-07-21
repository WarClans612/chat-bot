import urllib.request
import json

def grab_data():

#connect to cwb api
	urll = 'http://opendata2.epa.gov.tw/AQX.json'
	fp = urllib.request.urlopen(urll)
	data_list = json.loads(fp.read().decode('utf-8'))
	fp.close()
	
	return data_list

def get_pm25(Location_name):
	data_list = grab_data()
	for data in data_list:
		if data["County"] == Location_name:
			return data["PM2.5"]
	
if __name__ == "__main__":
	pm25 = get_pm25("新竹市")
	print(pm25)