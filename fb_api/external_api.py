import urllib.request
import json
from fb_api.fb_config import Google_Maps_Geocoding_API_key

mapping = {'台東縣': '臺東縣', '基隆': '基隆市', '臺南': '臺南市', '新北': '新北市', '台北市': '臺北市', '台中': '臺中市', '馬祖': '連江', '台中市': '臺中市', '台南市': '臺南市', '台北': '臺北市', '金門': '金門縣', '澎湖': '澎湖縣', '台東': '臺東縣', '桃園': '桃園市', '苗栗': '苗栗縣', '臺東': '臺東縣', '臺北': '臺北市', '臺中': '臺中市', '連江': '連江縣', '屏東': '屏東縣', '彰化': '彰化縣', '新竹': '新竹市', '花蓮': '花蓮縣', '高雄': '高雄市', '嘉義': '嘉義市', '南投': '南投縣', '宜蘭': '宜蘭縣', '台南': '臺南市', '雲林': '雲林縣'}


def get_area(location):
    google_api_url = 'https://maps.googleapis.com/maps/api/geocode/json?key='+Google_Maps_Geocoding_API_key+'&language=zh-TW&latlng='
    target_url = google_api_url+str(location['lat'])+','+str(location['long'])
    fp = urllib.request.urlopen(target_url)
    raw_data = json.loads(fp.read().decode('utf-8'))
    fp.close()
    area1 = ""
    area2 = ""
    area3 = ""
    for addr in raw_data['results'][0]['address_components']:
        if addr['types'][0] == 'administrative_area_level_1':
            area1 = addr['long_name']
        elif addr['types'][0] == 'administrative_area_level_2':
            area2 = addr['long_name']
        elif addr['types'][0] == 'administrative_area_level_3':
            area3 = addr['long_name']
        
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
    
if __name__ == "__main__":
    location = {}
    location['lat'] = 25.0339639
    location['long'] =  121.5644722
    county, area = get_area(location)
    print (county, " " ,area)
    
