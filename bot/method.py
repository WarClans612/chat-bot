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

def get_score(q_keywords, weighting_method):
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
if __name__ == '__main__':
	scores_sorted = get_score('天氣', 'probability')
	top_question_num = scores_sorted[0]
	print(top_question_num[0])