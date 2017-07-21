### Implemented using Python 3.5.2 (Anaconda 4.1.1) -- 64bit
PORT = 25555
DEBUG = False

from datetime import date, datetime
import json

from eve import Eve
from flask import jsonify, request

from api.mongodb import *
from api.utilities import *
from bot import bot_function as bot

app = Eve()
FOLDER = '/mnt/50C6F7D9C6F7BD72/@Experiments/academia/'

@app.route('/')
@app.route('/welcome')
@app.route('/help')
@app.route('/hello')
def hello_world():
    welcome = """
    Welcome to the Academia Sinica Project's REST API Server.\n
    Please use the following route to access the features.\n
    /qa/<question> : Asking question\n
    """
    # print(welcome)
    return welcome

@app.route('/find')
def find_keywords():
    client, db = open_connection()
    keywords = find_many_keywords(db)
    close_connection(client)
    return str(keywords)

@app.route('/qa/<question>')
def qa_handling(question):
    answer, words, scores = bot.qa_answering(question, answers, keyword_set)
    ip = request.remote_addr
    now = datetime.now()
    output = json.dumps({'question':question, 'answer':answer, 'keywords':words, 'client':ip, 'time':now.timestamp()})
    try:
        result = bytes(output, 'utf-8')
        result = result.decode('unicode-escape')
        # print(result)
        folder = FOLDER + '/log/'
        make_sure_path_exists(folder)
        filename = 'qa_log_{}.txt'.format(date.today())
        write_to_file(folder + filename, result)
        # print('write to file: {}'.format(filename))
    except Exception as ex:
        print(str(ex))
    return output

if __name__ == '__main__':
    ### Init QA Engine
    global answers, keyword_set
    filename = FOLDER + '/bot/QA.txt'
    questions, answers = bot.open_qa_file(filename)
    stop_words_filename = FOLDER + '/bot/extra_dict/stop_words.txt'
    idf_filename = FOLDER + '/bot/extra_dict/idf.txt.big'
    keywords, keyword_set, num_of_keyword = bot.init_jieba(stop_words_filename, idf_filename, questions)

    ### Eve webserver
    app.run(port=PORT, host='0.0.0.0', debug=DEBUG)
