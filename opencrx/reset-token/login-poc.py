import requests
import re
proxies = {
    'http': '127.0.0.1:8080',
    'https': '127.0.0.1:8080'
}
session = requests.session()

url = "http://opencrx:8080/opencrx-core-CRX/ObjectInspectorServlet"
get_params = '?loginFailed=false'
res = session.get(url+get_params, allow_redirects=True, proxies=proxies)
print(res.status_code)
print("==================================")
print(res.cookies)
print("==================================")
#print(res.content)
print("==================================")
url = "http://opencrx:8080/opencrx-core-CRX/j_security_check"
data = {"j_username": "guest", "j_password": "donkey12345"}
res = session.post(url, data=data, allow_redirects=True, proxies=proxies)
pattern = re.compile('window.*;') # extract out window.href='redirct_url'
result = pattern.findall(res.text)
pattern = re.compile("(?<=')(.*?)(?=')") # extract out redirect url
result = pattern.findall(result[0])
res = session.get(result[0], allow_redirects=True, proxies=proxies)

if 'Logoff&nbsp;guest' in str(res.text):
    print('apples')