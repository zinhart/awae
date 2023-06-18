# Remote Debugging & Source code recovery
- java apps
    - WEB-INF\lib contains jar files that we can feed into jd-gui.
    - After opening the jar file in question in jd-gui, to get all of the .java files: File > Save All Sources menu
    - Java web applications can be packaged in several different file formats, such as JARs, WARs, and EARs. All three of these file formats are essentially ZIP files with different extensions.
        - Java Archive (JAR) files are typically used for stand-alone applications or libraries.
        - Web Application Archive (WAR) files are used to collect multiple JARs and static content, such as HTML, into a single archive.
        - Enterprise Application Archive (EAR) files can contain multiple JARs and WARs to consolidate multiple web applications into a single file.
            - EAR files include an application.xml file that contains deployment information, which includes the location of external libraries within the META-INF directory
    - There are two general ways to analyze a java application
        1. Look at the deployment descriptor to understand how the application maps urls to servlets
        2. Start looking with the JSP files. This works because __JSP's mix java and html and are good places to look for authentication logic__
- Dotnet apps
    - To change from release mode to debug mode
        - This
            - [assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
        - Becomes
            - This 
                - [assembly: Debuggable(DebuggableAttribute.DebuggingModes.Default | DebuggableAttribute.DebuggingModes.DisableOptimizations | DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints | DebuggableAttribute.DebuggingModes.EnableEditAndContinue)]
        - The menu option is found by right clicking the assembly(DLL) and going to "Edit Assembly Attributes (C#)".
          It can also be reached via the "Edit" menu.
          - Afterwards we need to click on the Compile button and finally go to "File > Save Module"
    - As a side note when the IIS worker process starts it will not load the assemplies (DLLS) from C:\inetpub\wwwroot\dotnetnuke\bin\DotNetNuke.dll for example.
      It will load the assemblies from C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Temporary ASP.NET Files\dotnetnuke\
      So that is the file that we will attach to when debugging
    - In terms of actually debugging the application, the process that we need to attach to is __w3wp.exe__ which is the IIS worker process. 
      If __w3wp.exe__ is not found then browse to the application using a web broswer and then try again. This will trigger IIS to start the appropriate worker process.
    - After attaching to the correct process in the correct DLL , the next step is to pause execution at the appropriate module.
       - This can be found in
            - Debug => Wiundows => Modules
                - We then right click on any module and hit "Open All modules".
    - At this point we will be fully able to set break points at any location in the code.
    - Correct setup can be validate with break points. 
# Database Logging
- Particulary important when debugging sql injections, we may want to include how to accomplish this in the common databases
- Mariadb & Mysql
    - File is found at: /etc/mysql/my.cnf
        - Uncomment the lines
            - general_log_file
            - general_log
        - restart the mysql service
#  Email simulation
- See erpnext configuring the smtp server
# Vulns
## Websockets
Poshwebsocketclient module - done
## SQLI
- template script for blind conditional sqli - same thing as below but will need to check request length rather than timing query
- template script for blind timing based sqli - done for mysql & postgres
- Order by injection: https://portswigger.net/support/sql-injection-in-the-query-structure
- Dealing with collation errors
    - In general we should simply extract the collation from the database
        > SELECT COLLATION_NAME FROM information_schema.columns WHERE TABLE_NAME = "tablename" AND COLUMN_NAME = "name";
    - The modified sql statement now becomes
        > SELECT name COLLATE  'value extracted' FROM __Auth;
    - See the erpnext-auth-bypass for an example of how to get around any collation issues
- Hsqldb rce via stored procedures see opencrx.
    - The most important thing here is the ability to find a suitable function to call.
## XSS/CSRF/XXE
- postgres largeobject injection javascript
    - Most importantly scaling multiple fetches with reduce example. This one is important for writing concise exploits that depend on requests being executed in a specific order - done
- internal webapplication enumeration via javascript
- csrf
    - https://zinhart.io/csrf
- xss
    - python cors server for hosting all of the payloads -done
    - it's __important to spray ALL editable fields with xss payloads ***AND*** keep our eyes open for anybuilt in functions which may block XSS__. It may be that there are protections on a low priviledge part of the application but not on admin side.
- xxe
    - https://zinhart.io/xxe
    - xxe scripts for reading files/folder contents - done
    - In some languages, like PHP, XXE vulnerabilities can even lead to remote code execution. In Java, however, we cannot execute code with just an XXE vulnerability.
## LFI & Path Traversal
- The combination of both of these is useful for obtaining source code of the application in blackbox scenario and ultimately turning it into a whitebox scenario
- payload of all things has the best resource to testing this
## Deserialization
- python example - done
    - The main thing here is realizing the format of a serialized objects in python
        - base64 serialized objects begin with gASV
        - The best function to use in deserialization exploits is the __reduce__ function. See the example.
    - The other thing that is important to keep in mind is that there may not be a 1-1 code execution.
        - For example, we may be able to inject an object with a magic method in the destructor and in the destructor a file write is performed. In this example it would be possible to write to a webshell as a method of rce, but there would NOT be direct code execution.
- java example - done
    - ysoserial example and jar files placed in exam.
    - The most common gadget is common collections
- dotnet example
    - An example against XML Serializer with the exanded wrapper class has been placed in the exam folder.
    - The easiest way to achieve this however would be with ysoserial.net
    - A somewhat random side note, we can create a base64 powershell compliant encoded command in pure linux tools with
        > iconv -f ASCII -t UTF-16LE powershellcmd.txt | base64 | tr -d "\n" 
## SSRF
- http://zinhart.io/ssrf
Powershell Enumeration scripts

## SSTI
- payload of all things page for guidance
- include examples of ssti bypasses
## Weak Hashing
- Javascript Example
## TypeJuggling
- python script - done
- powershell script - not necesarry because itertools is superior
- The basic concept that makes type juggling possible in php
    - If the string does not contain any of the characters '.', 'e', or 'E' and the numeric value fits into integer type limits (as defined by PHP_INT_MAX), the string will be evaluated as an integer. In all other cases it will be evaluated as a float.
    - The value is given by the initial portion of the string. If the string starts with valid numeric data, this will be the value used. Otherwise, the value will be 0 (zero). Valid numeric data is an optional sign, followed by one or more digits (optionally containing a decimal point), followed by an optional exponent. The exponent is an 'e' or 'E' followed by one or more digits.
    - so 'magic' php strings typically begin with 0e and the a series of digits.
- The main value of at least as far as the AWAE/EXAM will is sha1 & md5 hashes of values that form a 'magic' php string of the form 0e123456789
## Prototype pollution
- example with offsec challenge I did
# Blacklist/Whitelist Filter bypasses
- Mostly can fool this by different encodings of the restricted string.
    - Mostly:
        - hex encoding
        - url enconding
# Tricks
    -  Parameter Pollution / Parameter       Tampering
        - a php method of information disclosure (e.g gaining the webroot in a blackblox scenario)
            - use an array in a parameter and hopefully force the application to leak the webroot
                - relies on display_errors being enable in the php.ini
# Auth Bypass
Most likely to be:
- XSS/CRSF
- SQLI
    - if we can steal a password hash via sqli it's worth it to check if we can perform a pass the hash
    - also keep an eye out for conditional based errors with cookies
- Timing error via guessable hash
    - this can be combined with blind sqli where we steal the hash
- SSRF to access a protected resource
- php type juggling in the context of a session authentication
    - particularly when can control both sides of an equation/expression    
    - it should be noted that php7 has improved implicit conversion rules in order to minimize some fo the potential loose comparison problems but this does __NOT__ affect magic strings of the 0e1234546 form.
- weak cookie logic
- path traversal/lfi to download sensitive files
# Auth Bypass Chains
- Sqli => token theft => auth bypass
# RCE
Most likely to be:
- File uploads
    - e.g if we can write a webshell to a public location
- SSTI
- SQLI
- Deserialization
- xxe to read sensitive files
    - maybe pull db auth creds/ssh keys/ etc
- SSRF
    - examples
        - writing a webshell to a externally reachable path
        - plugin injection
        - xxe

I think that the most important thing to keep in mind is that for the exam there will be the chaining of all of the vulns above in order to create an exploit.
# Full Chains
- sqli => auth bypass => rce via file upload
- type juggling => auth bypass => file upload bypass => rce
- time based blind sqli => stacked queries => rce via copy to / rce via postgres extensions/large object
- black list filter bypass via hex encoding => rce 
- unauthenticated deserialization
- sqli => leak user info => stealing password reset token => authbypass => ssti => rce
- password reset => auth bypass => xxe (file inclusion  & directory listing) => stealing credentials (tomcat-users.xml for example) => database auth => hsql stored procedures => file write => webshell => rce
- phishing => dom based xss => session riding => auth bypass => command injection via websockets
- phishing => csrf with cors => auth bypass => uploadable scripts -> rce 
- phishing => blind csrf => auth bypass => uploadable scripts -> rce
- insecure defaults (api key in source code) => auth bypass => uploadable scripts -> rce
- http verb tampering => blind ssrf => auth bypass => credential theft via xss => plugins => rce
- xss => session riding => auth bypass => xxe to ready sensitive files => postgres large object => rce
- timing error => sqli => steal password hash (it this case it was crackable) => auth bypass => xxe to ready sensitive files => postgres large object => rce
- guest account creation => time based blind sqli via websockets => admin token extraction from db => auth bypass => ssti => rce
- guest account creation => time based blind sqli via websockets => admin token extraction from db => auth bypass => command inject to right a sshkey to the filesystem => rce
- weak authentication via local storage => auth bypass => file inclusion & directory listing =>source code exfil => deserialization => ssh key written to local file system => rce.
- xss => session riding => auth bypass => malicious plugin => webshell => rce
# Remote Debugging
- java
- php
- .net
- node