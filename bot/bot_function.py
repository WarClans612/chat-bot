#!/usr/bin/python

import jieba
import jieba.analyse
from pymongo import MongoClient
import bot_config
import re

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
	words = jieba.analyse.extract_tags(question, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
	return words
		
def sensor_handler(handle_code):
	rain_bound = [20]
	temperature_bound = [20,30]
	air_quality_bound = [10,15,25,35]
	temperature, rainfull_prob = get_weather()
	air_quality = get_air_quality()
	if handle_code == 1 :
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
	elif handle_code == 2:
		if rainfull_prob < rain_bound[0]:
			answer_code = 1
		else:
			answer_code = 2
	elif handle_code == 3:
		if air_quality < air_quality_bound[0]:
			answer_code = 1
		elif air_quality < air_quality_bound[1]:
			answer_code = 2
		elif air_quality < air_quality_bound[2]:
			answer_code = 3
		else:
			answer_code = 4
	elif handle_code == 4:
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
		print("[err: no such handle_code]")
		
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	A_template = db.handle_table.find_one({'handle_code':handle_code, 'answer_code':answer_code })['A_template']
	replace_temperature = "#temperature#"
	replace_rainfull_prob = "#rainfull_prob#"
	answer = re.sub(replace_temperature, str(temperature), A_template)
	answer = re.sub(replace_rainfull_prob, str(rainfull_prob), answer)
	return answer
	
def get_answer(question_num):
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	handle_code = db.question_table.find_one({'question_num':question_num})['handle_code']
	
	if handle_code == 0 : #general QA
		answer = db.answer_table.find_one({'question_num':question_num})['answer']
	else : #sensor related QA
		answer = sensor_handler(handle_code)
	return answer

def get_weather():
	temperature = 30
	rainfull_prob = 50
	return temperature, rainfull_prob
	
def get_air_quality():
	air_quality = 18
	return air_quality
	
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