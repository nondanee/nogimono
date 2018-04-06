import asyncio
import hashlib, base64, time, random
from . import toolbox
from aiohttp import web
from aiohttp_session import get_session

@asyncio.coroutine
def route(request):

    session = yield from get_session(request)

    if request.content_type != "application/x-www-form-urlencoded":
        session.clear()
        return web.HTTPBadRequest()

    data = yield from request.post()

    if 'nickname' in data:
        nickname = data['nickname']
    else:
        return web.HTTPBadRequest()

    if 'password' in data:
        password = data['password']
        hash_password = hashlib.md5(password.encode("utf-8")).hexdigest().upper()
    else:
        return web.HTTPBadRequest()

    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()

        yield from cursor.execute('''
            SELECT 
            id 
            FROM 
            user 
            WHERE nickname = %s 
            and password = %s 
            and status = 1
        ''',(nickname,hash_password))

        out = yield from cursor.fetchone()
        yield from cursor.close()
        connect.close()

        if out:
            session["uid"] = out[0]
            return web.Response()
        else:
            session.clear()
            return web.HTTPForbidden()

            # token_string = "{uid}:{time}:{random}".format(
            #     uid = str(uid).zfill(8),
            #     time = str(int(time.time())),
            #     random = str(random.randint(0,9999)).zfill(4)
            # )

            # token = hashlib.sha1(token_string.encode("utf-8")).hexdigest()
            # print(token)
