import hashlib, string, itertools, re
from itertools import takewhile
prefix_length = 5
hashes = []
for word in map(''.join, itertools.product(string.ascii_lowercase,repeat=int(prefix_length))):
    print(word)
    # application specific calculation of pre-hash value here
    hash_val = word 
    # calculate the hash here, might not be sha1 so pay attention
    hash = hashlib.sha1(str(hash_val).encode('utf-8')).hexdigest()[5:20]
    # criteria to find a hash the of the form 0x0XXX to cuck php's 
    if re.match(r'0+[eE]\d+$', hash):
        hashes.append(hash_val)
        if (len(hashes) >= 10):
            break
