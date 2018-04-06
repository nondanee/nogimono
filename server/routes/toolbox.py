import asyncio
import pytz, datetime, time, json
from aiohttp import web

def time_utc(time_set):
    # jptime = timeset.replace(tzinfo=pytz.timezone("Asia/Tokyo"))
    cn_time = pytz.timezone('Asia/Shanghai').localize(time_set)
    return cn_time.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def jsonify(json_dict):
    return json.dumps(json_dict,ensure_ascii=False,sort_keys=True,indent=4)

def time_stamp(time_set):
    return int(time.mktime(time_set.timetuple()))

def type_to_number(type_string):
    check = {"all":0,"blog":1,"magazine":2,"news":3}
    if type_string in check: return check[type_string]

def number_to_type(type_number):
    check = {1:"blog",2:"magazine",3:"news"}
    if type_number in check: return check[type_number]

def javaify(code=200,message="ok",data=None):
    json_dict = {
        "code": code,
        "message": message,
        "data": data
    }
    return web.Response(
        text = jsonify(json_dict),
        content_type = "application/json",
        charset = "utf-8"
    )

@asyncio.coroutine
def access(cursor,uid,token):
    permit = yield from cursor.execute('''
        SELECT * FROM user WHERE id = %s AND token = %s
    ''',(uid,token))
    if not permit:
        return False
    else:
        return True


@asyncio.coroutine
def headers_access(cursor,headers):
    if "uid" not in headers:
        return False
    elif "token" not in headers:
        return False
    try:
        uid = int(headers["uid"])
        token = headers["token"]
    except:
        return False
    permit = yield from access(cursor,uid,token)
    if not permit:
        return False
    else:
        return True