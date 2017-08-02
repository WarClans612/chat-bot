from flask import Flask
import jieba
import jieba.analyse
PORT = 25555
DEBUG = False


app = Flask(__name__)

@app.route('/')
def index():
	fw = open('tmp.txt','w')
	fw.close()
	return "<p>Hello World!</p>"
	
@app.route('/segmentation/<question>')
def segmentation_words(question):
	topK = 20
	withWeight = False
	allowPOS = ()
	words = jieba.analyse.extract_tags(question, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
	return "/".join(words)
	
if __name__ == '__main__':
	### init jieba settings ###
	jieba.set_dictionary('extra_dict/zh-tw_dict.txt')
	jieba.load_userdict("extra_dict/my_dict.txt")
	jieba.load_userdict("extra_dict/location_dict.txt")
	jieba.analyse.set_stop_words('extra_dict/stop_words.txt')
	jieba.analyse.set_idf_path('extra_dict/idf.txt.big')
	
	### start api ###
	app.run(port=PORT, debug=DEBUG)

