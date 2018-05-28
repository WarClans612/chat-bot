from flask import Flask, request
import ssl
import json
app = Flask(__name__)

from fb_api.fb_config import VERIFICATION_CODE
from fb_api.get_callback import *

@app.route('/')
def index():
    return "<p>Hello World!</p>"
    
@app.route('/privacypolicy')
def privacy():
    text = "<p>[臺灣生活環境小幫手 隱私權政策]</p>\
            <p>登入: 直接對話即可使用</p>\
            <p>隱私權: 只會取得使用者所傳之訊息</p>\
            <p>訂閱: 可以在對話框輸入[訂閱]來選擇訂閱內容,且一天一項目只會打擾一次</p>\
            <p>      並且可以輸入[取消訂閱]來做取消動作</p>\
            <p>      決不在違反使用者意願情況下主動傳訊息</p>\
            "
    return text
    
@app.route('/webhook', methods=["GET"])
def fb_webhook():
    verify_token = request.args.get('hub.verify_token')
    if VERIFICATION_CODE == verify_token:
        return request.args.get('hub.challenge')
    return 'Invalid verification token'
        
@app.route('/webhook', methods=['POST'])
def fb_receive_message():
    print(request.data.decode('utf8'))
    return 'hi'
    message_entries = json.loads(request.data.decode('utf8'))['entry']
    for entry in message_entries:
        for item in entry['messaging']:
            user_id = item['sender']['id']
            if item.get('message'):
                message = item['message']
                if message.get('quick_reply'):
                    get_quick_reply(user_id,message['quick_reply']['payload'])
                elif message.get('text'):
                    text = message['text']
                    get_text(user_id,text)
                elif message.get('attachments'):
                    attachments = message['attachments']
                    for att in attachments :
                        if att['type'] == "location":
                            get_location(user_id,att['payload']['coordinates'])
    return "Hi"