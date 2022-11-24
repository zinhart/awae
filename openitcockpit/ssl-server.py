import http.server, ssl, argparse

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        print(body)
        self.send_response(200)
        self.end_headers()
        '''
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        '''




parser = argparse.ArgumentParser()
parser.add_argument('--host', help='IP to Listen On', required=True)
parser.add_argument('--port', help='Port to Listen on', required=True)
parser.add_argument('--cert', help='cert file (PEM file)', required=True)
args = parser.parse_args()

print(F"Serving HTTPS on {args.host} port {args.port} (http://{args.host}:{args.port}/) ...")
#httpd = http.server.HTTPServer((args.host,int(args.port)), http.server.SimpleHTTPRequestHandler)
httpd = http.server.HTTPServer((args.host,int(args.port)), HTTPRequestHandler)
sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
sslctx.check_hostname = False # If set to True, only the hostname that matches the certificate will be accepted
sslctx.load_cert_chain(certfile=F'{args.cert}') # we would also suple the keyfile here
httpd.socket = sslctx.wrap_socket(httpd.socket, server_side=True)
httpd.serve_forever()
'''
httpd = http.server.HTTPServer((args.host,int(args.port)), http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.SSLContext.wrap_socket(httpd.socket,server_side=True, certfile=F'{args.cert}', ssl_version=ssl.PROTOCOL_TLS)
httpd.serve_forever()
'''
