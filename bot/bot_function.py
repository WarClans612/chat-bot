#!/usr/bin/python

import jieba
import jieba.analyse

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