#!/usr/bin/python3.4

from pymongo import MongoClient
import operator   
import bot_config

def get_score(q_keywords, weighting_method):
	###connect to DB:"bot"
	db_url = bot_config.db_url 
	db_name = bot_config.db_name
	client = MongoClient(db_url)
	db = client[db_name]
	
	# = db.statistic_data.find_one({'name':'num_of_questions'})['value']
	scores = {}
	
	for row in db.QAKset.find():
		scores[row['answer']] = 0
	
	if weighting_method == 'frequency':
		for row in db.QAKset.find():
			row_keyword_list = row['keyword_list']
			for k in q_keywords:
				if k in row_keyword_list:
					scores[row['answer']] = scores[row['answer']] +1
	elif weighting_method == 'ratio':
		for row in db.QAKset.find():
			row_keyword_list = row['keyword_list']
			row_num_of_keyword = row['num_of_keyword']
			for k in q_keywords:
				if k in row_keyword_list:
					scores[row['answer']] = scores[row['answer']] + (1/row_num_of_keyword)
	elif weighting_method == 'probability':
		for row in db.QAKset.find():
			row_keyword_list = row['keyword_list']
			for k in q_keywords:
				if k in row_keyword_list:
					scores[row['answer']] = scores[row['answer']] + db.keyword_data.find_one({'keyword':k})['weight']
	else:
		print("not such weighting_method")
		
	scores_sorted = sorted(scores.items(),key = operator.itemgetter(1),reverse = True)
	return scores_sorted
#return schema : [('bb', 4), ('aa', 3), ('cc', 2), ('dd', 1)]
if __name__ == '__main__':
	get_score('天氣', 'probability')