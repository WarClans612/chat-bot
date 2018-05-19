import urllib.request
import json
from taiwan_city import mapping
from fb_api.fb_config import Google_Maps_Geocoding_API_key

def get_area(location):
    '''
        This function is used to connect to google API and retrieve location name for coordinate
        It will return 2 most probable name available
        If the query failed, then it will return "不知道",""
    '''
    google_api_url = 'https://maps.googleapis.com/maps/api/geocode/json?key='+Google_Maps_Geocoding_API_key+'&language=zh-TW&latlng='
    target_url = google_api_url+str(location['lat'])+','+str(location['long'])
    with urllib.request.urlopen(target_url) as fp:
        raw_data = json.loads(fp.read().decode('utf-8'))
    area1 = ""
    area2 = ""
    area3 = ""
    for addr in raw_data['results'][0]['address_components']:
        address_type = addr['types'][0]
        address_name = addr['long_name']
        if address_type == 'administrative_area_level_1':
            area1 = address_name
        elif address_type == 'administrative_area_level_2':
            area2 = address_name
        elif address_type == 'administrative_area_level_3':
            area3 = address_name
        
    if mapping.get(area1):
        area1 = mapping[area1]
    if mapping.get(area2):
        area2 = mapping[area2]
    if mapping.get(area3):
        area3 = mapping[area3]
        
    if area1 != "":
        return area1,area3
    elif area2 != "":
        return area2,area3
        
    return "不知道",""
    
