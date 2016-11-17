### Implemented using Python 3.5.2 (Anaconda 4.1.1) -- 64bit
#!/usr/bin/python

import jieba
import jieba.analyse
from flask import jsonify

topK = 20
withWeight = False
allowPOS = ()

def open_qa_file(filename):
    question = []
    answer = []
    i = 0
    with open(filename, 'r', encoding='utf8') as fr:
        for line in fr:
            text = line.strip()
            if i % 2 == 0:
                question.append(text)
            else:
                answer.append(text)
            i += 1
    return question, answer

def init_jieba(stop_words_filename, idf_filename, question):
    jieba.analyse.set_stop_words(stop_words_filename)
    jieba.analyse.set_idf_path(idf_filename)

    keyword_set = [] 
    num_of_keyword = []
    keywords = []

    for i in range(len(question)):
        words = jieba.analyse.extract_tags(question[i], topK=topK, withWeight=withWeight, allowPOS=allowPOS)
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
    try:
        index = max(scores, key=scores.get)
    except:
        index = 0
    return answer_db[index], words, scores

if __name__ == '__main__':
    ### Init QA from file
    filename = './QA.txt'
    questions, answers = open_qa_file(filename)

    ### Initialize jieba
    stop_words_filename = './extra_dict/stop_words.txt'
    idf_filename = './extra_dict/idf.txt.big'
    keywords, keyword_set, num_of_keyword = init_jieba(stop_words_filename, idf_filename, questions)

    ### Testing the module
    question = ['正常人的血糖應該多少才正常?']
    for q in question:
        a = qa_answering(q, answers, keyword_set)
        print(q)
        print(a)
        print(q.encode('utf-8'))
        print(a.encode('utf-8'))
        print(a.encode('utf-8').decode('utf-8'))