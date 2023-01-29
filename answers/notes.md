
## Open Ports Basic
```
PORT     STATE SERVICE        REASON
22/tcp   open  ssh            syn-ack ttl 63
80/tcp   open  http           syn-ack ttl 63
8000/tcp open  http-alt       syn-ack ttl 63
8888/tcp open  sun-answerbook syn-ack ttl 63
```
## Open Ports Detailed
```
PORT     STATE SERVICE         VERSION
22/tcp   open  ssh             OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 ecff7c128f46307f58d5d699b60b7f9a (RSA)
|   256 35a6b439ed98461c17c7204731e759b0 (ECDSA)
|_  256 5eb2a8a315121c5eb4ab3224789fb741 (ED25519)
80/tcp   open  http            Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: A N S W E R S
8000/tcp open  jdwp            Java Debug Wire Protocol (Reference Implementation) version 1.8 1.8.0_252
|_jdwp-info: ERROR: Script execution failed (use -d to debug)
8888/tcp open  sun-answerbook?
```
### Port 22 SSH
Won't bother since the point of this is whitebox
### Port 8000 Java Debug Wire Protocol
Two existing exploits on searchsploit, need to confirm version numbers
- https://www.exploit-db.com/exploits/33789 (metasploit)
- https://www.exploit-db.com/exploits/46501 (python)
### Port 8888 APACHE
Seems to be a mirror of port 80 because the same webapplication is running
### Port 80 APACHE
#### Browsing From a Blackbox Perspective
##### Interesting Pages
- /question
  - What's interesting here is that the form on this page specifically allows html tags, and furthermore requests the user not abuse this functionality.  
  The allowed tags are:
    - em
    - strong
    - code
  It's probably worth it to bruteforce this page with html tags and see what is truly restricted.  
  In addition with the source code it's worth investigating how the filter mechanism works.
- /search?query= is an interesting potential sink
- /profile
  - Visiting this page produces the following error:
    > Whitelabel Error Page
    > This application has no explicit mapping for /error, so you are seeing this as a fallback.
    > Sun Jan 29 15:02:46 UTC 2023
    > There was an unexpected error (type=Not Found, status=404).
    > No message available
  Which after googling this hints that we are dealing with a springboot application which is a java framework
- /profile/:id
  - We can iterate through all of the user accounts by visiting: /profile/:id
  - There are 8 profiles total
  - /profile/0 redirects to index
  - /profile/9 redirects to index
  - /profile/1 is The administrator account
    - This account also seems to have a "Moderator" role
  - /profile/5 is "CARL"
    - This account also seems to have a "Moderator" role
  - /profile/7 is "EVELYN"
     - This account also seems to have a "Moderator" role
- /login
  - We have the capability to do username enumeration because:
    - With a valid username and incorrect password we receive an option to send a magic link. Specifically the text is:
      > Complex password got you down? Get a magic link and sign in from your email!
      - When in this menu the menu icon dropdown menu changes to include the options of:
        > Change Password
          - Unfortunately without the magic link clicking this returns us to /login
        > Logout
          - Clicking logout returns us to /login?logout
    - An incorrect password returns a message of
      > Please enter a valid username and password
##### Potential users
- CARL
- Evelyn
- Demetri
- ALICE
- Bob
- ADMIN
- Franco
- Anonymous
