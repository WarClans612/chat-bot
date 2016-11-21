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
	
def qa_answering(sentence, answer_db, keyword_set_db):
	scores = {}
	words = jieba.analyse.extract_tags(sentence, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
	for word in words:
		for i in range(len(keyword_set_db)):
			if word in keyword_set_db[i]:
				found = scores.get(i)
				if found is None:
					found = 0
				found += 1.0 / len(keyword_set_db[i])
				scores[i] = found
	if len(scores) == 0:
		return default_message
	else:
		index = max(scores, key=scores.get)
		# value = max(scores, key=scores.get)
		return answer_db[index]

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
	
def keyword_set_recording(question_set, answer_set, keyword_set, file_recording):
	with open(file_recording,'w',encoding='utf8') as fw:
		for i in range(len(question_set)):
			fw.write('Q: '+question_set[i]+'\n')
			fw.write('K: '+'/'.join(keyword_set[i])+'\n')
			fw.write('A: '+answer_set[i]+'\n\n')
		
if __name__ == '__main__':
	### Init QA from file
	filename = '課程抵免QA.txt'
	question_set, answer_set = open_qa_file(filename)

	### Initialize jieba
	stop_words_filename = 'extra_dict/stop_words.txt'
	idf_filename = 'extra_dict/idf.txt.big'
	keywords, keyword_set, num_of_keyword = init_jieba(stop_words_filename, idf_filename, question_set)
	
	#keyword_set_recording
	file_recording = '課程抵免.recording'
	keyword_set_recording(question_set, answer_set, keyword_set, file_recording)