#!/usr/bin/python

import jieba
import jieba.analyse
from pymongo import MongoClient
import math
import bot_config

topK = 20
withWeight = False
allowPOS = ()
default_message = "找不到符合的答案"

def open_qa_file(filename):
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
		num_of_keyword.append(len(words))
		keywords.extend(words)
	# print(keywords)
	# print(keyword_set)

	return keywords, keyword_set, num_of_keyword
	
if __name__ == '__main__':
	### Init QA from file
	filename = bot_config.QAset
	sensor_filename = bot_config.sensorQAset
	question_set, question_num_set, answer_set, answer_num_set = open_qa_file(filename)
	sensor_question_set, sensor_question_num_set, sensor_answer_set, sensor_answer_num_set = open_sensor_qa_file(sensor_filename)

	### Initialize jieba
	stop_words_filename = 'extra_dict/stop_words.txt'
	idf_filename = 'extra_dict/idf.txt.big'
	jieba.set_dictionary('extra_dict/zh-tw_dict.txt')
	jieba.load_userdict("extra_dict/my_dict.txt")
	jieba.load_userdict("extra_dict/location_dict.txt")
	keywords, keyword_set, num_of_keyword = init_jieba(stop_words_filename, idf_filename, question_set)
	sensor_keywords, sensor_keyword_set, sensor_num_of_keyword = init_jieba(stop_words_filename, idf_filename, sensor_question_set)
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
	
	### Save into DB table:"question_table"
	collect = db['question_table']
	
	for i in range(len(question_set)):
		data = {"question": question_set[i],
				"question_num": question_num_set[i],
				"keyword_list": keyword_set[i],
				"num_of_keyword": num_of_keyword[i],
				"handle_code": 0,
				"type": "general"
				}
		collect.insert_one(data)
	sensor_start_num = question_num_set[len(question_num_set)-1] + 1
	for i in range(len(sensor_question_set)):
		data = {"question": sensor_question_set[i],
				"question_num": sensor_start_num + sensor_question_num_set[i],
				"keyword_list": sensor_keyword_set[i],
				"num_of_keyword": sensor_num_of_keyword[i],
				"handle_code": sensor_question_num_set[i] + 1 ,
				"type": "sensor"
				}
		collect.insert_one(data)
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
	print("[answer_table]")
	for post in collect.find():
		print (post)
	
	### Save into DB table:"handle_table"
	collect = db['handle_table']
	flag_handle = 0
	for i in range(len(sensor_answer_set)):
		if flag_handle != (sensor_answer_num_set[i] + 1) :
			flag_handle = sensor_answer_num_set[i] + 1
			answer_code = 1
		else:
			answer_code += 1 
		data = {"handle_code": sensor_answer_num_set[i] + 1,
				"answer_code": answer_code,
				"A_template": sensor_answer_set[i]
			}
		collect.insert_one(data)
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