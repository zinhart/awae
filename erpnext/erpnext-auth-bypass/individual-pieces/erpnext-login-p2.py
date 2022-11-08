# pretty much a validation that we are in a logged in state
import requests

session = requests.session()

burp0_url = "http://erpnext:8000/desk"
burp0_cookies = {"user_id": "zeljka.k%40randomdomain.com", "user_image": "", "full_name": "Zeljka%20Kola%C5%A1inac", "sid": "28496c782ae0ae39614dc9aeaadce8e06e41c883cdda7f5e775158b9", "system_user": "yes"}
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Referer": "http://erpnext:8000/", "Upgrade-Insecure-Requests": "1"}
session.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)