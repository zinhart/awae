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
- ***$search_field*** through ***$_POST['myFriendsOnly']***
- All this can be found in: ***ATutor/mods/_standard/social/index_public.php***  
In terms of alternate methods of auth bypasses in ***include/login_functions.inc.php*** we can:
- poision the cookie (line 60)
- poison submit1