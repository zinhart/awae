# Vulns
## Websockets
Poshwebsocketclient module - done
## SQLI
- template script for blind conditional sqli
- template script for blind timing based sqli - done for mysql
## XSS/CSRF/XXE
- postgres largeobject injection javascript
    - Most importantly scaling multiple fetches with reduce example. This one is important for writing concise exploits -done
- internal webapplication enumeration javascript
- xxe scripts for reading files/folder contents - done
- python cors server for hosting all of the payloads -done
## LFI & Path Traversal
- The combination of both of these is useful for obtaining source code of the application in blackbox scenario and ultimately turning it into a whitebox scenario
## Deserialization
- python example
    - The main thing here is realizing the format of a serialized objects in python
        - base64 serialized objects begin with gASV
        - The best function to use in deserialization exploits is the __reduce__ function. See the example.
- java example
- dotnet example
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