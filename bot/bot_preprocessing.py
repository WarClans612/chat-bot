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
		
if __name__ == '__main__':
	### Init QA from file
	filename = bot_config.QAset
	question_set, answer_set = open_qa_file(filename)

	### Initialize jieba
	stop_words_filename = 'extra_dict/stop_words.txt'
	idf_filename = 'extra_dict/idf.txt.big'
	keywords, keyword_set, num_of_keyword = init_jieba(stop_words_filename, idf_filename, question_set)
	
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	
	### drop all tables to reset
	db.drop_collection('QAKset')
	db.drop_collection('keyword_data')
	db.drop_collection('statistic_data')
	
	### Save into DB table:"QAKset"
	collect = db['QAKset']

	for i in range(len(question_set)):
		data = {"question": question_set[i],
				 "answer": answer_set[i],
				 "keyword_list": keyword_set[i],
				 "num_of_keyword": num_of_keyword[i]}
		collect.insert_one(data)
	
	print("[QKAset]")	
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
		weight = 1 - prob
		data_k = { "keyword": row['keyword'] }
		data_new = { "$set" : { "prob": prob , "weight": weight} }
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