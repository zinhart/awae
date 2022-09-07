#!/usr/bin/python
import imaplib, sys

if len(sys.argv) != 2:

        print("(+) usage: %s <target>" % sys.argv[0])
        sys.exit(-1)
        
atmail = sys.argv[1]

print(atmail)

box = imaplib.IMAP4(atmail, 143)
box.login("admin@offsec.local","123456")
box.select('Inbox')

typ, data = box.search(None, 'ALL')

for num in data[0].split():
        box.store(num, '+FLAGS', '\\Deleted')
        
box.expunge()
box.close()
box.logout()
