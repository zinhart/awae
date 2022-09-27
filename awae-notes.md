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