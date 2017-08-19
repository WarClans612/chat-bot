#!/usr/bin/python

import jieba
import jieba.analyse
from pymongo import MongoClient
import sys
import bot_config
import re
#import WeatherAPI.weather as weather
#import my_pm25 as pm25
from sensor_fetch import get_pm25 as pm25
from sensor_fetch import get_weather as weather
from sensor_fetch import get_uvi as UVI
from datetime import datetime #datetime.datetime
import urllib.request
import urllib.parse

topK = 20
withWeight = False
allowPOS = ()
default_message = "找不到符合的答案"

def open_qa_file(filename):
	question_set = []
	answer_set = []
	i = 0
	with open(filename, 'r', encoding='utf8') as fr:
		for line in fr:
			text = line.strip()
			if i % 2 == 0:
				question_set.append(text)
			else:
				answer_set.append(text)
			i += 1
	return question_set, answer_set

def init_jieba(stop_words_filename, idf_filename, question_set):
	jieba.analyse.set_stop_words(stop_words_filename)
	jieba.analyse.set_idf_path(idf_filename)

	keyword_set = [] 
	num_of_keyword = []
	keywords = []

	for i in range(len(question_set)):
		words = jieba.analyse.extract_tags(question_set[i], topK=topK, withWeight=withWeight, allowPOS=allowPOS)
		keyword_set.append(words)
		num_of_keyword.append(len(words))
		keywords.extend(words)
	# print(keywords)
	# print(keyword_set)

	return keywords, keyword_set, num_of_keyword
	

def qa_questoining(source, file_questioning):
	questions = []
	if source=='input':
		text = input("==>")
		questions.append(text)
	elif source=='file':
		with open(file_questioning, 'r', encoding='utf8') as fr:
			for line in fr:
				text = line.strip()
				questions.append(text)
	else:
		print('error in qa_questoining : no such source!')
	return questions
	
def qa_answering(sentence, answer_db, keyword_set_db):
	scores = {}
	words = jieba.analyse.extract_tags(sentence, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
	match_keywords = []
	for word in words:
		for i in range(len(keyword_set_db)):
			if word in keyword_set_db[i]:
				match_keywords.append(word)
				found = scores.get(i)
				if found is None:
					found = 0
				found += 1.0 / len(keyword_set_db[i])
				scores[i] = found
	print ('keywords in questioning: '+'/'.join(words))
	print ('keywords matched: '+'/'.join(match_keywords))
	print ()
	if len(scores) == 0:
		return default_message
	else:
		index = max(scores, key=scores.get)
		print (str(scores.get(index))+'%matched')
		return answer_db[index]
		
		
def segment(question):
	#words = jieba.analyse.extract_tags(question, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
	urll = bot_config.segment_api_url
	target_url = urllib.request.Request(urll+ urllib.parse.quote(question.strip(), safe=''))
	fp = urllib.request.urlopen(target_url)
	data_list = fp.read().decode('utf-8')
	fp.close()
	words = data_list.split("/")
	return words
		
def sensor_handler(handle_code,slots):
	rain_bound = [20]
	temperature_bound = [20,30]
	air_quality_bound = [10,15,25,35]
	uvi_bound = [6,8,11]
	temperature = 0
	rainfull_prob = 0
	air_quality = 0
	uvi = 0
	if handle_code == "WEATHER" :
		temperature, rainfull_prob = get_weather(slots)
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
	elif handle_code == "RAIN":
		temperature, rainfull_prob = get_weather(slots)
		if rainfull_prob < rain_bound[0]:
			answer_code = 1
		else:
			answer_code = 2
	elif handle_code == "PM25":
		air_quality = get_air_quality(slots)
		if air_quality < air_quality_bound[0]:
			answer_code = 1
		elif air_quality < air_quality_bound[1]:
			answer_code = 2
		elif air_quality < air_quality_bound[2]:
			answer_code = 3
		else:
			answer_code = 4
	elif handle_code == "GOOUT":
		air_quality = get_air_quality(slots)
		temperature, rainfull_prob = get_weather(slots)
		uvi = get_uvi(slots)
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
	elif handle_code == "UVI":
		uvi = get_uvi(slots)
		if uvi < uvi_bound[0]:
			answer_code = 1
		elif uvi < uvi_bound[1]:
			answer_code = 2
		elif uvi < uvi_bound[2]:
			answer_code = 3
		else:
			answer_code = 4
	else: 
		print("[err: no such handle_code -- ",handle_code," ]")
		
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	A_template = db.handle_table.find_one({'handle_code':handle_code, 'answer_code':answer_code })['A_template']
	answer = A_template
	replace_mapping = {"#temperature#" : temperature , "#rainfull_prob#" : rainfull_prob , "#pm25#" : air_quality , "#uvi#" : uvi}
	for pattern in replace_mapping :
		if re.search(pattern, A_template) != None:
			answer = re.sub(pattern, str(replace_mapping[pattern]), answer)
	if "time" in slots:
		if slots["time"] == "now":
			time_str = "目前"
		else:
			time_str = "明天"
	else:
		time_str = "目前"
	answer = re.sub("#time#", str(time_str), answer)
	answer = re.sub("#space#", str(slots["space"]), answer)
	return answer

def sensor_handler_for_subscription(handle_code,slots):
	air_quality_bound = [10,15,25,35]
	uvi_bound = [6,8,11]
	air_quality = 0
	uvi = 0
	answer_code = 0
	if handle_code == "PM25":
		air_quality = get_air_quality(slots)
		if air_quality < air_quality_bound[0]:
			answer_code = 1
		elif air_quality < air_quality_bound[1]:
			answer_code = 2
		elif air_quality < air_quality_bound[2]:
			answer_code = 3
		else:
			answer_code = 4
	elif handle_code == "UVI":
		uvi = get_uvi(slots)
		if uvi < uvi_bound[0]:
			answer_code = 1
		elif uvi < uvi_bound[1]:
			answer_code = 2
		elif uvi < uvi_bound[2]:
			answer_code = 3
		else:
			answer_code = 4
	else: 
		print("[err: no such handle_code -- ",handle_code," ]")
		
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	A_template = db.handle_table.find_one({'handle_code':handle_code, 'answer_code':answer_code })['A_template']
	answer = A_template
	replace_mapping = { "#pm25#" : air_quality , "#uvi#" : uvi}
	for pattern in replace_mapping :
		if re.search(pattern, A_template) != None:
			answer = re.sub(pattern, str(replace_mapping[pattern]), answer)
	if "time" in slots:
		if slots["time"] == "now":
			time_str = "目前"
		else:
			time_str = "明天"
	else:
		time_str = "目前"
	answer = re.sub("#time#", str(time_str), answer)
	answer = re.sub("#space#", str(slots["space"]), answer)
	if answer_code <= 2 :
		answer = None
	return answer
	
def get_answer(question_num,slots):
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	handle_code = db.question_table.find_one({'question_num':question_num})['handle_code']
	type = db.question_table.find_one({'question_num':question_num})['type']
	
	if type == "general" : #general QA
		answer = db.answer_table.find_one({'question_num':question_num})['answer']
	else : #sensor related QA
		answer = sensor_handler(handle_code,slots)
	return answer

def get_weather(slots):
	#temperature = 30
	#rainfull_prob = 50
	# if "space" not in slots:
		# slots["space"] = "新竹市"
	if "time" not in slots:
		slots["time"] = "now"
	item = weather.get_weather(Location_name = slots["space"], time = slots["time"])
	temperature = float(item["temperature"])
	rainfull_prob = int(item["rainfull_prob"])
	return temperature, rainfull_prob
	
def get_air_quality(slots):
	#air_quality = 18
	air_quality = pm25.get_pm25(slots["space"])
	return float(air_quality)
	
def get_uvi(slots):
	uvi = UVI.get_uvi(slots["space"])
	return float(uvi)
	
def get_slots(words):
	slots = {}
	rest_words = []
	rest_words.extend(words)
	country_name = ['宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣', '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市', '基隆市', '新竹縣', '新竹市', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '嘉義市', '屏東縣']
	country_nickname = ['宜蘭', '花蓮', '臺東', '台東', '台東縣', '澎湖', '金門', '連江', '臺北', '台北', '台北市', '新北', '桃園', '臺中', '台中', '台中市', '臺南', '台南', '台南市', '高雄', '基隆', '新竹', '苗栗', '彰化', '南投', '雲林', '嘉義', '屏東', '馬祖']
	mapping = {'台東縣': '臺東縣', '基隆': '基隆市', '臺南': '臺南市', '新北': '新北市', '台北市': '臺北市', '台中': '臺中市', '馬祖': '連江', '台中市': '臺中市', '台南市': '臺南市', '台北': '臺北市', '金門': '金門縣', '澎湖': '澎湖縣', '台東': '臺東縣', '桃園': '桃園市', '苗栗': '苗栗縣', '臺東': '臺東縣', '臺北': '臺北市', '臺中': '臺中市', '連江': '連江縣', '屏東': '屏東縣', '彰化': '彰化縣', '新竹': '新竹市', '花蓮': '花蓮縣', '高雄': '高雄市', '嘉義': '嘉義市', '南投': '南投縣', '宜蘭': '宜蘭縣', '台南': '臺南市', '雲林': '雲林縣'}
	time_name = ['今天','現在','明天']
	for i in words:
		if i in country_name:
			slots["space"] = i
			rest_words.remove(i)
		if i in country_nickname:
			slots["space"] = mapping[i]
			rest_words.remove(i)
	for i in words:
		if i in time_name:
			if i in ['今天','現在']:
				slots['time'] = 'now'
				rest_words.remove(i)
			elif i in ['明天']:
				slots['time'] = 'next'
				rest_words.remove(i)
	return slots, rest_words
	
if __name__ == '__main__':
	### Init QA from file
	filename = '課程抵免QA.txt'
	question_set, answer_set = open_qa_file(filename)

	### Initialize jieba
	stop_words_filename = 'extra_dict/stop_words.txt'
	idf_filename = 'extra_dict/idf.txt.big'
	keywords, keyword_set, num_of_keyword = init_jieba(stop_words_filename, idf_filename, question_set)

	### Testing the module
	#questions = ['我想問課程抵免問題?', '我可以抵免計算機網路概論嗎?', '我想要問要幾分才可以抵免?']
	#source from file
	"""
	source = 'file'
	file_questioning = '課程抵免_questions.txt'
	questions = qa_questoining(source, file_questioning)
	for q in questions:
		a = qa_answering(q, answer_set, keyword_set)
		print(q)
		print(a)
		print()
	"""
	#source from input
	source = 'input'
	file_questioning = ''
	while 1==1:
		questions = qa_questoining(source, file_questioning)
		q = questions[0]
		a = qa_answering(q, answer_set, keyword_set)
		print('Q: '+q)
		print('A: '+a)
		print()
	
	"""
	#source from training set
	questions = question_set
	for q in questions:
		a = qa_answering(q, answer_set, keyword_set)
		print(q)
		print(a)
		print()
	"""