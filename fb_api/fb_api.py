from flask import Flask, request
import ssl
import json
app = Flask(__name__)

from fb_api_config import verification_code
import get_callback as GET

@app.route('/')
def index():
	fw = open('tmp.txt','w')
	fw.close()
	return "<p>Hello World!</p>"
	
@app.route('/image')
def image():
	return render_template('image.html')
	
@app.route('/webhook', methods=["GET"])
def fb_webhook():
	verify_token = request.args.get('hub.verify_token')
	if verification_code == verify_token:
		return request.args.get('hub.challenge')
		
@app.route('/webhook', methods=['POST'])
def fb_receive_message():
	message_entries = json.loads(request.data.decode('utf8'))['entry']
	for entry in message_entries:
		for item in entry['messaging']:
			user_id = item['sender']['id']
			if item.get('message'):
				message = item['message']
				if message.get('quick_reply'):
					GET.get_quick_reply(user_id,message['quick_reply']['payload'])
				elif message.get('text'):
					text = message['text']
					GET.get_text(user_id,text)
				elif message.get('attachments'):
					attachments = message['attachments']
					for att in attachments :
						if att['type'] == "location":
							GET.get_location(user_id,att['payload']['coordinates'])
	return "Hi"
	
if __name__ == '__main__':
	ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
	ssl_ctx.load_cert_chain('ssl/certificate.crt', 'ssl/private.key')
	ssl_ctx.load_verify_locations(cafile='ssl/ca_bundle.crt')
	app.run(host='0.0.0.0',  port= 443, debug=True, ssl_context=ssl_ctx)