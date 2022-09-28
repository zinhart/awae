from email import message
import imaplib
import email
from email.header import decode_header
import re
import webbrowser
from xmlrpc.client import Boolean
import os
def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)
def get_imap(imap_server:str, ssl:Boolean = False):
    return imaplib.IMAP4_SSL(imap_server) if ssl else imaplib.IMAP4(imap_server)
def get_message_count(imap_client:imaplib, folder:str):
    #imap_client.login(username, password)
    status, messages = imap_client.select(folder)
    return int(messages[0])
def get_messages(imap_client:imaplib, folder:str):
    message_count = get_message_count(imap_client=imap_client, folder=folder)
    #print(message_count)
    ret = []
    for i in range( message_count, 0, -1):
        res, msg = imap_client.fetch(str(i), "(RFC822)")
        #print(i)
        msg_obj = {'subject': '', 'from': '', 'body': ''}
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                #print("Subject:", subject)
                #print("From:", From)
                msg_obj['subject'] = subject
                msg_obj['from'] = From
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                            msg_obj['body'] = body
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            #print(body)
                            msg_obj['body'] = body
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        #print(body)
                        msg_obj['body'] = body
                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    #open(filepath, "w").write(body)
                    # open in the default browser
                    #webbrowser.open(filepath)
                #print("="*100)
        ret.append(msg_obj)
    # close the connection and logout
    imap_client.close()
    imap_client.logout()
    return ret

def example():
    imap_client = get_imap("atmail")
    imap_client.login('dlv@offsec.local', '123456')
    msgs = get_messages(imap_client,'inbox')
    #print(msgs)
    print(msgs[0]['body'])
    links = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    print(re.findall(links, msgs[0]['body']))

