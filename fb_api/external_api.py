import urllib.request
import json
from fb_api_config import Google_Maps_Geocoding_API_key

def get_area(location):
	urll = 'https://maps.googleapis.com/maps/api/geocode/json?key='+Google_Maps_Geocoding_API_key+'&language=zh-TW&latlng='
	target_url = urll+str(location['lat'])+','+str(location['long'])
	fp = urllib.request.urlopen(target_url)
	pure_data = json.loads(fp.read().decode('utf-8'))
	fp.close()
	area1 = ""
	area2 = ""
	area3 = ""
	for addr in pure_data['results'][0]['address_components']:
		if addr['types'][0] == 'administrative_area_level_1':
			area1 = addr['long_name']
		elif addr['types'][0] == 'administrative_area_level_2':
			area2 = addr['long_name']
		elif addr['types'][0] == 'administrative_area_level_3':
			area3 = addr['long_name']
		
	if area1 != "":
		return area1+area3
	elif area2 != "":
		return area2+area3
		
	return "不知道"
