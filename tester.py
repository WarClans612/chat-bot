### Implemented using Python 3.5.2 (Anaconda 4.1.1) -- 64bit
import http.client
from urllib.parse import quote_plus
import chardet

HOST = '140.113.213.14'
PORT = 25555

def request(conn, parameter):
    # print(parameter)
    conn.request('GET', parameter)
    response = conn.getresponse()

    status = response.status
    reason = response.reason
    print(status, reason)

    if status == 200:
        ### Data is in byte array format
        data = response.read()
        enc = chardet.detect(data)
        result = bytes(data.decode(enc['encoding']), 'utf-8').decode('unicode-escape')
        print(result)

if __name__ == '__main__':
    conn = http.client.HTTPConnection(HOST, PORT)
    # request(conn, '/hello')
    pre = '/qa/'
    # q = '正常人的血糖應該多少才正常?'
    qs = ['正常人的血糖應該多少才正常?', '高血壓前期的血壓值是多少?', '你好']
    for q in qs:
        param = pre + q
        ### Original parameter
        print(param)
        ### Change to HTML format (encoding)
        enc_param = quote_plus(param)
        print(enc_param)
        ### Sending request to the API server
        request(conn, enc_param)