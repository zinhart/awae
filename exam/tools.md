# Vulns
## Websockets
Poshwebsocketclient module
## SQLI
- template script for blind conditional sqli
- template script for blind timing based sqli
## XSS/CSRF/XXE
- postgres largeobject injection javascript
- internal webapplication enumeration javascript
- xxe scripts for reading files/folder contents
- python cors server for hosting all of the payloads
## LFI & Path Traversal
- The combination of both of these is useful for obtaining source code of the application in blackbox scenario and ultimately turning it into a whitebox scenario
## Deserialization
- python example
- java example
## SSRF
Powershell Enumeration scripts
## SSTI
- payload of all things page for guidance
## Weak Hashing
- Javascript Example
## TypeJuggling
- python script
- powershell script
## Prototype pollution
- example with offsec challenge I did
# Blacklist/Whitelist Filter bypasses
- Mostly can fool this by different encodings of the restricted string.
    - Mostly:
        - hex encoding
        - url enconding
# Auth Bypass
Most likely to be:
- XSS/CRSF
- SQLI
- Timing error via guessable hash
# RCE
Most likely to be:
- SSTI
- SQLI
- Deserialization
# Remote Debugging
- java
- php
- .net
- node