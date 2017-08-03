#!/usr/bin/python3.4

from pymongo import MongoClient
import operator   
import bot_config

###weighting_method:
# 'frequency'
# 'ratio'
# 'probability'
# 'weight_e'
# 'fre_prob'
# 'combination'

def get_score(q_keywords, weighting_method): ### "prob" contains some question
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	
	# = db.statistic_data.find_one({'name':'num_of_questions'})['value']
	scores = {}
	scores_fre = {}
	scores_prob = {}
	
	for row in db.question_table.find():
		scores[row['question_num']] = 0
		scores_fre[row['question_num']] = 0
		scores_prob[row['question_num']] = 0
	
	if weighting_method == 'frequency':
		for row in db.question_table.find():
			row_keyword_list = row['keyword_list']
			for k in q_keywords:
				if k in row_keyword_list:
					scores[row['question_num']] = scores[row['question_num']] +1
	elif weighting_method == 'ratio':
		for row in db.question_table.find():
			row_keyword_list = row['keyword_list']
			row_num_of_keyword = row['num_of_keyword']
			for k in q_keywords:
				if k in row_keyword_list:
					scores[row['question_num']] = scores[row['question_num']] + (1/row_num_of_keyword)
	elif weighting_method == 'probability':
		for row in db.question_table.find():
			row_keyword_list = row['keyword_list']
			for k in q_keywords:
				if k in row_keyword_list:
					scores[row['question_num']] = scores[row['question_num']] + db.keyword_data.find_one({'keyword':k})['weight_prob']
	elif weighting_method == 'weight_e':
		for row in db.question_table.find():
			row_keyword_list = row['keyword_list']
			for k in q_keywords:
				if k in row_keyword_list:
					scores[row['question_num']] = scores[row['question_num']] + db.keyword_data.find_one({'keyword':k})['weight_e']
	elif weighting_method == 'fre_prob':
		for row in db.question_table.find():
			row_keyword_list = row['keyword_list']
			for k in q_keywords:
				if k in row_keyword_list:
					scores_fre[row['question_num']] = scores_fre[row['question_num']] +1
					scores_prob[row['question_num']] = scores_prob[row['question_num']] + db.keyword_data.find_one({'keyword':k})['weight_prob']
		scores_fre_sorted = sorted(scores_fre.items(),key = operator.itemgetter(1),reverse = True)
		top_fre = scores_fre_sorted[0][1]
		for s in scores_fre_sorted:
			if s[1] != top_fre:
				break
			scores[s[0]] = scores_prob[s[0]]
	elif weighting_method == 'combination':
		for row in db.question_table.find():
			row_keyword_list = row['keyword_list']
			for k in q_keywords:
				if k in row_keyword_list:
					scores_fre[row['question_num']] = scores_fre[row['question_num']] +1
					scores_prob[row['question_num']] = scores_prob[row['question_num']] + db.keyword_data.find_one({'keyword':k})['weight_prob']
		scores_fre_sorted = sorted(scores_fre.items(),key = operator.itemgetter(1),reverse = True)
		scores_prob_sorted = sorted(scores_prob.items(),key = operator.itemgetter(1),reverse = True)
		top_fre = scores_fre_sorted[0][1]
		for s in scores_fre_sorted:
			if s[1] != top_fre:
				break
			scores[s[0]] += 1
		top_prob = scores_prob_sorted[0][1]
		for s in scores_prob_sorted:
			if s[1] != top_prob:
				break
			scores[s[0]] += 1
	else:
		print("not such weighting_method")
		
	scores_sorted = sorted(scores.items(),key = operator.itemgetter(1),reverse = True)
	return scores_sorted
#return schema : [('bb', 4), ('aa', 3), ('cc', 2), ('dd', 1)]

def integrateQA(q_keywords):
	N = len(q_keywords)
	
	### connect to DB:"bot" ###
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	
	scores_fre_general = {}
	scores_fre_sensor = {}
	pass_general_list = []
	pass_sensor_list = []
	
	for row in db.question_table.find({'type': "general"}):
		scores_fre_general[row['question']] = 0
		row_keyword_list = row['keyword_list']
		for k in q_keywords:
			if k in row_keyword_list:
				scores_fre_general[row['question']] = scores_fre_general[row['question']] +1
	for row in db.question_table.find({'type': "general"}):
		tmp_prob = scores_fre_general[row['question']] / row['num_of_keyword']
		if tmp_prob > 0.6:
			pass_general_list.append(row['question'])
	
	for row in db.question_table.find({'type': "sensor"}):
		scores_fre_sensor[row['question']] = 0
		row_keyword_list = row['keyword_list']
		for k in q_keywords:
			if k in row_keyword_list:
				scores_fre_sensor[row['question']] = scores_fre_sensor[row['question']] +1
	for row in db.question_table.find({'type': "sensor"}):
		tmp_prob = scores_fre_sensor[row['question']] / row['num_of_keyword']
		if tmp_prob == 1 :
			pass_sensor_list.append(row['question'])
	
	if len(pass_general_list)!= 0 :
		general_most_fre = scores_fre_general[pass_general_list[0]]
		general_most_q = pass_general_list[0]
		for i in pass_general_list:
			tmp_fre = scores_fre_general[i]
			if tmp_fre > general_most_fre:
				general_most_fre = tmp_fre
				general_most_q = i
				
	if len(pass_sensor_list)!= 0 :
		sensor_most_fre = scores_fre_sensor[pass_sensor_list[0]]
		sensor_most_q = pass_sensor_list[0]
		for i in pass_sensor_list:
			tmp_fre = scores_fre_sensor[i]
			if tmp_fre > sensor_most_fre:
				sensor_most_fre = tmp_fre
				sensor_most_q = i
	
	
	
	if len(pass_general_list)!=0 and len(pass_sensor_list)!= 0:
		if sensor_most_fre>=general_most_fre:
			type = "sQA"
		else:
			type = "gQA"
	elif len(pass_general_list)==0 and len(pass_sensor_list)!= 0:
		type = "sQA"
	elif len(pass_general_list)!=0 and len(pass_sensor_list)== 0:
		if (general_most_fre / N) > 0.6:
			type = "gQA"
		else:
			type = "neither"
	else: 
		type = "neither"
	
	if type == "sQA":
		q_num = db.question_table.find_one({'question': sensor_most_q})['question_num']
	elif type == "gQA":
		q_num = db.question_table.find_one({'question': general_most_q})['question_num']
	else:
		q_num = 0
		
	return type, q_num
	

if __name__ == '__main__':
	### test get_score ###
	# scores_sorted = get_score('天氣', 'probability')
	# top_question_num = scores_sorted[0]
	# print(top_question_num[0])
	
	
	### test integrateQA ###
	question = ["今天","天氣"]
	result = integrateQA(question)
	print(result)