# AWAE NOTES
## Atmail
url parameter required to make file path upload work
Crsf plugin transferring files as hex
## Atutor
Alternate injection paths in index_public.php
```bash
 cat /var/www/html/ATutor/mods/_standard/social/index_public.php | grep '$_GET\|$_POST' --color
```
In the course material we poison search friends through: ***$_GET['q']*** but,  
we could also use:
- ***$search_field*** through ***$_GET['search_friends']***
    - we can trigger a sql error with ***GET /ATutor/mods/_standard/social/index_public.php?search_friends='*** so that is the starting point for this path.
- ***$search_field*** through ***$_POST['myFriendsOnly']***
- All this can be found in: ***ATutor/mods/_standard/social/index_public.php***  
In terms of alternate methods of auth bypasses in ***include/login_functions.inc.php*** we can:
- poision the cookie (line 60)
- poison submit1
    - this one requires minimal changes. submit1,form1_password_hidden,form1_login
    ```bash
    form_login_action=true&form_course_id=0&form1_password_hidden=c7b25645b5bc2b1927b4c4b0247ec2495be3ce6f&p=&form1_login=teacher&form1_password=&submit1=Login&token=
    ```
Atutor type juggling weak hash TOCTOU
magic hash attacks
https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use
## ManageEngine
Improve the regex used earlier to locate all the SELECT SQL queries in the code base in order to limit the results to only those which include string concatenation and a WHERE clause.
```sql
select.*where.*\+
```
```sql
^.*select\s\* from.*\swhere.*\s".*$
```
```sql
(doGet.*|doPost.*)
```
```sql
(doGet.*|doPost.*)+(\n\S.*)+
```
We want to search for doGet|doPost functions that contain a sql query with a where clause that has some string concatenation, I've found the best way to do this is to chain greps instead of one mega regexp(and I tried).
Using the script below we are able to reduce the searchspace to 8 files.
```bash
for i in $( grep -RlP '(doGet.*|doPost.*)' manage-engine/com/adventnet/ ); do grep -lP 'select.+from.+where.+\+' $i ; done
```
The main thing with identifying where to search for sql injections in manage engine is to ***identify the attacker controllable portions of the application***. This turned out to be the ***doGet*** ***doPost*** methods of ***javax.servlet.http.HttpServletRequest;***. The second part changes from language/framework to language/framework put the concept is same, we look attacker controllable parts of the application(http requests/forms/etc) and use programming language/framework knowledge to narrow our search down. This is how we narrow the attack surface.
