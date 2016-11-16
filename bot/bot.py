#!/usr/bin/python

import jieba
import jieba.analyse


#question[] answer[] N
file = open('QA_examples.txt', 'r')
question = []
answer = []
data_Q = file.readline().strip()
data_A = file.readline().strip()
while data_Q:
    question.append(data_Q)
    answer.append(data_A)
    data_Q = file.readline().strip()
    data_A = file.readline().strip()
N=len(answer)
file.close()


#keyword_set[] num_of_keyword[]
jieba.analyse.set_stop_words("extra_dict/stop_words.txt")
jieba.analyse.set_idf_path("extra_dict/idf.txt.big");
keyword_set = [] 
num_of_keyword = []
keywords = []

for i in range(N):
    words = jieba.analyse.extract_tags(question[i], topK=20, withWeight=False, allowPOS=())
    keyword_set.append(words)
    num_of_keyword.append(len(words))
    keywords.extend(words)
	

sentence = input("-->")
#words = jieba.cut(sentence, cut_all=False)
words = jieba.analyse.extract_tags(sentence, topK=20, withWeight=False, allowPOS=())

flag = []
for i in range(N):
    flag.append(0)
for word in words:
    if word in keywords:
        for i in range(N):
            if word in keyword_set[i]:
                flag[i]=flag[i]+1
				
maxmatch = 0
ans_num = 0
for i in range(N):
    if maxmatch < (flag[i]/num_of_keyword[i]):
        maxmatch = (flag[i]/num_of_keyword[i])
        ans_num = i
print(answer[ans_num])
