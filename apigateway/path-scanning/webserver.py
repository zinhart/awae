from flask import Flask
from flask import request
from flask import make_response
from flask import send_from_directory
import urllib.parse
import logging
from datetime import datetime
log = logging.getLogger('werkzeug')
log.disabled = True


app = Flask(__name__)

def parse(data):
    return urllib.parse.unquote(data)
def now():
    now = datetime.now()
    # dd/mm/YY H:M:S
    return now.strftime("%d/%m/%Y %H:%M:%S")

@app.route('/<path:path>')
def send_report(path):
    return send_from_directory('html-extramile-payloads', path)
@app.route('/callback',methods=['GET','POST'])
def success():
    print(request.remote_addr, '-', now(), '-', parse(request.query_string))
    return '',200
@app.route('/callback_json',methods=['GET','POST'])
def success():
    print(request.remote_addr, '-', now(), '-', parse(request.query_string), request.body)
    return '',200
@app.route('/error',methods=['GET','POST'])
def error():
    print(request.remote_addr, '-', now(), '-', parse(request.query_string))
    return '',200

app.run('0.0.0.0',1080)