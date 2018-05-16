#!/usr/bin/python3.4

import operator
from pymongo import MongoClient
from bot import bot_config
from bot import util

def get_score(q_keywords, weighting_method):
    '''
        Calculating scores for given question and weigthing method
        weighting method --> frequency, ratio, probability, weight_e, fre_prob, combination
    '''
    method_list = ['frequency', 'ratio', 'probability', 'weight_e', 'fre_prob', 'combination']
    special_condition_method = ['fre_prob', 'combination']
    if weighting_method not in method_list:
        print("There is no such Weighting Method")
        return None

    #Start by connecting to database
    db = util.connect_to_database()

    #Explicit decalaration of needed dictionary
    scores = {}
    scores_fre = {}
    scores_prob = {}
    
    #Initialize needed dictionary
    for entry in db['question_table'].find():
        assigned_num = entry['question_num']
        scores[assigned_num] = 0
        #Only initialized if used
        if weighting_method in special_condition_method:
            scores_fre[assigned_num] = 0
            scores_prob[assigned_num] = 0

    #Calculate each scores depending on weighting method
    for entry in db['question_table'].find():
        assigned_num = entry['question_num']

        #Build needed dictionary to calculate scores
        entry_keyword_list = entry['keyword_list']
        entry_num_of_keyword = entry['num_of_keyword']
        for k in q_keywords:
            if k in entry_keyword_list:
                #Formula differs depending on weighting method
                if weighting_method == 'frequency':
                    scores[assigned_num] += 1
                elif weighting_method == 'ratio':
                    scores[assigned_num] += (1/entry_num_of_keyword)
                elif weighting_method == 'probability':
                    scores[assigned_num] += db['keyword_data'].find_one({'keyword':k})['weight_prob']
                elif weighting_method == 'weight_e':
                    scores[assigned_num] += db['keyword_data'].find_one({'keyword':k})['weight_e']
                elif weighting_method in special_condition_method:
                    scores_fre[assigned_num] += 1
                    scores_prob[assigned_num] += db['keyword_data'].find_one({'keyword':k})['weight_prob']

    #Futher calculation for special_condition_method to determine wanted scores
    if weighting_method in special_condition_method:
        #Preparing the sorted score
        scores_fre_sorted = sorted(scores_fre.items(),key = operator.itemgetter(1),reverse = True)
        scores_prob_sorted = sorted(scores_prob.items(),key = operator.itemgetter(1),reverse = True)
        
        #Calculating score for fre_prob
        if weighting_method == 'fre_prob':
            top_fre = scores_fre_sorted[0][1]
            for s in scores_fre_sorted:
                if s[1] != top_fre:
                    break
                scores[s[0]] = scores_prob[s[0]]
        #Calculating score for combination
        elif weighting_method == 'combination':
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

    '''
        Scores returned will be in sorted Non-increasing order
        return schema : [('bb', 4), ('aa', 3), ('cc', 2), ('dd', 1)]
    '''
    scores_sorted = sorted(scores.items(),key = operator.itemgetter(1),reverse = True)
    return scores_sorted

########################################################################################

def generate_pass_list(db, type, q_keywords, scores_fre, pass_list):
    '''
        The value of the two received argument(scores_fre and pass_list) is referenced
        Therefore the value will be changed direcly from the received dictionary
        The recieved dictionary is expected to be empty (not necessarily)
    '''
    
    #Determining threshold by type
    if type == 'general':
        q_threshold = bot_config.general_threshold
    elif type == 'sensor':
        q_threshold = bot_config.sensor_threshold
    elif type == 'i':
        q_threshold = bot_config.i_threshold
    else:
        return

    #Calculating scores for each of the question
    for entry in db['question_table'].find({'type': type}):
        scores_fre[entry['question']] = 0
        entry_keyword_list = entry['keyword_list']
        for k in q_keywords:
            if k in entry_keyword_list:
                scores_fre[entry['question']] += 1
    
    #Filter the question that pass the threshold values
    '''
        The loop is not combined with aboves loop to prevent 
        mistake in calculation if multiple entry['question'] exists
    '''
    for entry in db['question_table'].find({'type': type}):
        tmp_prob = scores_fre[entry['question']] / entry['num_of_keyword']
        if tmp_prob > q_threshold:
            pass_list.append(entry['question'])
            
def generate_prob(scores_fre, pass_list):
    '''
        The value of the two received argument(scores_fre and pass_list) is referenced
        Therefore the value will be changed direcly from the received dictionary
    '''
    #Initializes value
    most_fre = 0
    most_q = 0
    
    #Replace the value with highest if the list is available
    if len(pass_list)!= 0 :
        most_fre = scores_fre[pass_list[0]]
        most_q = pass_list[0]
        for entry in pass_list:
            tmp_fre = scores_fre[entry]
            if tmp_fre > most_fre:
                most_fre = tmp_fre
                most_q = entry
    return most_fre, most_q
    
def integrateQA(q_keywords):
    '''
        This function is used to determine type of the question
        and the corresponding question_num in the database
    '''
    
    #Start by connecting to database
    db = util.connect_to_database()
    
    scores_fre_general = {}
    scores_fre_sensor = {}
    scores_fre_i = {}
    pass_general_list = []
    pass_sensor_list = []
    pass_i_list = []
    
    #Generate pass list for the corresponding type of the question
    generate_pass_list(db, 'general', q_keywords, scores_fre_general, pass_general_list)
    generate_pass_list(db, 'sensor', q_keywords, scores_fre_sensor, pass_sensor_list)
    generate_pass_list(db, 'i', q_keywords, scores_fre_i, pass_i_list)
    
    #Calculate the highest frequeny question
    general_most_fre, general_most_q = generate_prob(scores_fre_general, pass_general_list)
    sensor_most_fre, sensor_most_q = generate_prob(scores_fre_sensor, pass_sensor_list)
    i_most_fre, i_most_q = generate_prob(scores_fre_i, pass_i_list)

    #Determine the type from the value of frequency above
    if len(pass_i_list)!=0:
        type = "iQA"
    elif len(pass_general_list)!=0 and len(pass_sensor_list)!= 0:
        if sensor_most_fre>=general_most_fre:
            type = "sQA"
        else:
            type = "gQA"
    elif len(pass_general_list)==0 and len(pass_sensor_list)!= 0:
        type = "sQA"
    elif len(pass_general_list)!=0 and len(pass_sensor_list)== 0:
        question_length = len(q_keywords)
        if (general_most_fre / question_length) > 0.6:
            type = "gQA"
        else:
            type = "neither"
    else: 
        type = "neither"
    
    #Determine the question_num of the value of frequency above
    if type == "sQA":
        q_num = db['question_table'].find_one({'question': sensor_most_q})['question_num']
    elif type == "gQA":
        q_num = db['question_table'].find_one({'question': general_most_q})['question_num']
    elif type == "iQA":
        q_num = db['question_table'].find_one({'question': i_most_q})['question_num']
    else:
        q_num = 0

    return type, q_num
