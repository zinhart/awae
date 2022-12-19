from flask import Flask
from flask import request
from flask import make_response
app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def hello_world():
    print('Headers')
    print(request.headers)
    #print("Cookies")
    #for keys, value in request.cookies.items():
    #    print(keys, ":", value)
    #print(request.data)
    #print(request.args)
    #print(request.form)
    #print(request.endpoint)
    print("Method: ",request.method)
    print("Remote Addr: ",request.remote_addr)
    return 'Hello, World!',200
@app.after_request
def after_request_func(response):
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        #response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
        response.headers.add('Access-Control-Allow-Methods',
                            'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)

    return response
### end CORS section
app.run('0.0.0.0',80)