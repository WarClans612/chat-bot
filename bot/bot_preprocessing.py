#!/usr/bin/python

import jieba
import jieba.analyse
from pymongo import MongoClient
import math
import bot_config
import json

topK = 20
withWeight = False
allowPOS = ()
default_message = "找不到符合的答案"

def open_qa_file(filename):
	question_set = []
	question_num_set = []
	answer_set = []
	answer_num_set = []
	i = 1
	flag_pre = 'N'
	with open(filename, 'r', encoding='utf8') as fr:
		for line in fr:
			text = line.strip()
			#"Q: question"
			if text[0] == 'Q':
				if flag_pre == 'A':
					i += 1
				question_set.append(text[3:])
				question_num_set.append(i)
				flag_pre = 'Q'
			elif text[0] == 'A':
				answer_set.append(text[3:])
				answer_num_set.append(i)
				flag_pre = 'A'
			else :
				print("[err in general_QAset: start not with Q: or A: ]")
	return question_set, question_num_set, answer_set, answer_num_set

def open_sensor_qa_file(filename):
	question_set = []
	question_num_set = []
	answer_set = []
	answer_num_set = []
	i = 0
	flag_pre = 'N'
	with open(filename, 'r', encoding='utf8') as fr:
		for line in fr:
			text = line.strip()
			#"Q: question"
			if text[0] == 'Q':
				if flag_pre == 'A':
					i += 1
				question_set.append(text[3:])
				question_num_set.append(i)
				flag_pre = 'Q'
			elif text[0] == 'A':
				answer_set.append(text[3:])
				answer_num_set.append(i)
				flag_pre = 'A'
			else :
				print("[err in sensor_QAset: start not with Q: or A: ]")
	return question_set, question_num_set, answer_set, answer_num_set	

def init_jieba(stop_words_filename, idf_filename, question_set):
	jieba.analyse.set_stop_words(stop_words_filename)
	jieba.analyse.set_idf_path(idf_filename)

	keyword_set = [] 
	num_of_keyword = []
	keywords = []

	for i in range(len(question_set)):
		words = jieba.analyse.extract_tags(question_set[i], topK=topK, withWeight=withWeight, allowPOS=allowPOS)
		keyword_set.append(words)
		if len(words) == 0:
			num_of_keyword.append(1)
		else:
			num_of_keyword.append(len(words))
		keywords.extend(words)
	# print(keywords)
	# print(keyword_set)

	return keywords, keyword_set, num_of_keyword
	
def sensor_data_init(sensor_start_num, sensor_filename):
	fr = open(sensor_filename,"r",encoding = "utf8")
	text = fr.read()
	j_data = json.loads(text)
	
	###for question_table
	sensor_keywords = []
	question_num = sensor_start_num
	data_list = []
	for item in j_data:
		for q in item["Q"]:
			data = {}
			data["type"] = "sensor"
			data["question_num"] =  question_num
			data["handle_code"] = item["H"]
			data["question"] = q
			keyword_list = jieba.analyse.extract_tags(q, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
			data["keyword_list"] =  keyword_list
			sensor_keywords.extend(keyword_list)
			data["num_of_keyword"] = len(keyword_list)
			data_list.append(data)
		question_num = question_num +1
	#print(data_list)
	#print(sensor_keywords)
	sensor_question_list = data_list
	
	###for handle_table
	data_list = []
	for item in j_data:
		answer_code = 1
		for a in item["A"]:
			data = {}
			data["handle_code"] = item["H"]
			data["answer_code"] = a["answer_code"]
			data["A_template"] = a["answer_template"]
			data_list.append(data)
			answer_code = answer_code +1
	#print(data_list)
	sensor_handle_list = data_list
	
	###for button_table
	data_list = []
	question_num = sensor_start_num
	for item in j_data:
		data = {}
		data["question_num"] = question_num
		data["button_list"] = item["B"]
		data_list.append(data)
		question_num = question_num +1
	#print(data_list)
	sensor_button_list = data_list
	
	i_start_num = question_num
	
	return sensor_keywords,sensor_question_list,sensor_handle_list,sensor_button_list, i_start_num
		
def i_data_init(i_start_num, i_filename):
	fr = open(i_filename,"r",encoding = "utf8")
	text = fr.read()
	j_data = json.loads(text)
	
	###for question_table
	i_keywords = []
	question_num = i_start_num
	data_list = []
	for item in j_data:
		for q in item["Q"]:
			data = {}
			data["type"] = "i"
			data["question_num"] =  question_num
			data["handle_code"] = item["H"]
			data["HL_code"] = item["HL"]
			data["question"] = q
			keyword_list = jieba.analyse.extract_tags(q, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
			data["keyword_list"] =  keyword_list
			i_keywords.extend(keyword_list)
			data["num_of_keyword"] = len(keyword_list)
			data_list.append(data)
		question_num = question_num +1
	#print(data_list)
	#print(sensor_keywords)
	i_question_list = data_list
	
	
	question_num = i_start_num
	###for handle_table
	data_list = []
	for item in j_data:
		data = {}
		data["question_num"] = question_num
		data["answer"] = item["A"]
		data_list.append(data)
		question_num = question_num +1
	#print(data_list)
	i_answer_list = data_list
	
	i_start_num = question_num
	
	return i_keywords,i_question_list,i_answer_list
		

	
if __name__ == '__main__':
	### Init QA from file
	filename = bot_config.QAset
	sensor_filename = bot_config.sensorQAset
	i_filename = bot_config.iQAset
	question_set, question_num_set, answer_set, answer_num_set = open_qa_file(filename)
	#sensor_question_set, sensor_question_num_set, sensor_answer_set, sensor_answer_num_set = open_sensor_qa_file(sensor_filename)

	### Initialize jieba
	stop_words_filename = 'extra_dict/stop_words.txt'
	idf_filename = 'extra_dict/idf.txt.big'

	jieba.set_dictionary('extra_dict/zh-tw_dict.txt')
	jieba.load_userdict("extra_dict/my_dict.txt")
	jieba.load_userdict("extra_dict/location_dict.txt")
	jieba.analyse.set_stop_words(stop_words_filename)
	jieba.analyse.set_idf_path(idf_filename)
	
	keywords, keyword_set, num_of_keyword = init_jieba(stop_words_filename, idf_filename, question_set)
	sensor_start_num = question_num_set[len(question_num_set)-1] + 1
	sensor_keywords,sensor_question_list,sensor_handle_list,sensor_button_list, i_start_num = sensor_data_init(sensor_start_num,sensor_filename)
	i_keywords,i_question_list,i_answer_list = i_data_init(i_start_num,i_filename)
	#sensor_keywords, sensor_keyword_set, sensor_num_of_keyword = init_jieba(stop_words_filename, idf_filename, sensor_question_set)
	keywords.extend(sensor_keywords)
	
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	
	### drop all tables to reset
	db.drop_collection('question_table')
	db.drop_collection('answer_table')
	db.drop_collection('handle_table')
	db.drop_collection('keyword_data')
	db.drop_collection('statistic_data')
	db.drop_collection('button_table')
	
	### Save into DB table:"question_table"
	collect = db['question_table']
	
	for i in range(len(question_set)):
		data = {"question": question_set[i],
				"question_num": question_num_set[i],
				"keyword_list": keyword_set[i],
				"num_of_keyword": num_of_keyword[i],
				"handle_code": "None",
				"type": "general"
				}
		collect.insert_one(data)
	for data in sensor_question_list:
		collect.insert_one(data)
	for data in i_question_list:
		collect.insert_one(data)
	# sensor_start_num = question_num_set[len(question_num_set)-1] + 1
	# for i in range(len(sensor_question_set)):
		# data = {"question": sensor_question_set[i],
				# "question_num": sensor_start_num + sensor_question_num_set[i],
				# "keyword_list": sensor_keyword_set[i],
				# "num_of_keyword": sensor_num_of_keyword[i],
				# "handle_code": sensor_question_num_set[i] + 1 ,
				# "type": "sensor"
				# }
		# collect.insert_one(data)
	"""
	data = {"question": "現在適合出門嗎?",
			 "question_num": 0,
			 #"answer": ["天氣和空氣品質都很好喔，很適合出門!","天氣不太好，不建議出門","空氣品質很差喔，不建議戶外活動"],
			 "keyword_list": ["現在","適合","出門"],
			 "num_of_keyword": 3,
			 "handle_code": 0 
			}
	"""
	print("[question_table]")	
	for post in collect.find():
		print (post)
	
	### Save into DB table:"answer_table"
	collect = db['answer_table']
	for i in range(len(answer_set)):
		data = {"question_num": answer_num_set[i],
				"answer": answer_set[i]
			}
		collect.insert_one(data)
	collect.insert(i_answer_list)
	print("[answer_table]")
	for post in collect.find():
		print (post)
	
	### Save into DB table:"handle_table"
	collect = db['handle_table']
	for data in sensor_handle_list:
		collect.insert_one(data)
	
	# flag_handle = 0
	# for i in range(len(sensor_answer_set)):
		# if flag_handle != (sensor_answer_num_set[i] + 1) :
			# flag_handle = sensor_answer_num_set[i] + 1
			# answer_code = 1
		# else:
			# answer_code += 1 
		# data = {"handle_code": sensor_answer_num_set[i] + 1,
				# "answer_code": answer_code,
				# "A_template": sensor_answer_set[i]
			# }
		# collect.insert_one(data)
	print("[handle_table]")
	for post in collect.find():
		print (post)
		
	### Save into DB table:"keyword_data"
	collect = db['keyword_data']
	for i in range(len(keywords)):
		data_k = { "keyword": keywords[i] }
		data_f = { "$inc":{"frequency": 1} }
		collect.update_one(data_k,data_f,upsert=True)
	num_of_keywords = collect.count()
	
	for row in collect.find():
		prob = row['frequency'] / len(question_set)
		weight_prob = 1 - prob
		weight_e = math.exp(2*weight_prob)
		data_k = { "keyword": row['keyword'] }
		data_new = { "$set" : { "prob": prob , "weight_prob": weight_prob , "weight_e": weight_e} }
		collect.update_one(data_k,data_new,upsert=True)
		
	print("[keyword_data]")
	for post in collect.find():
		print (post)
		
	### Save into DB table:"statistic_data"
	collect = db['statistic_data']
	data = {"name": "num_of_frequency",
			"value": len(keywords)}
	collect.insert_one(data)
	data = {"name": "num_of_keywords",
			"value": num_of_keywords}
	collect.insert_one(data)
	data = {"name": "num_of_questions",
			"value": len(question_set)}
	collect.insert_one(data)

	print("[statistic_data]")
	for post in collect.find():
		print (post)
		
	### Save into DB table:"button_table"
	collect = db['button_table']
	for data in sensor_button_list:
		collect.insert_one(data)

	print("[button_table]")
	for post in collect.find():
		print (post)
		
		
	###save init_num
	collect = db["question_table"]
	init_question = collect.find_one({"handle_code":"WEATHER"})["question_num"]
	collect = db["user_information"]
	result = collect.update_many({}, { "$set": { "question_num": init_question } })
