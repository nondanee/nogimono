import asyncio
import random, datetime
from . import toolbox
from aiohttp import web
from aiohttp_session import get_session


@asyncio.coroutine
def route(request):

    session = yield from get_session(request)
    if 'uid' in session:
        uid = session['uid']
    else:
        return web.HTTPForbidden()

    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()

        post = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")

        try:
            yield from cursor.execute('''
                SELECT id FROM feed WHERE uid = %s AND type = 0
            ''',(uid,))

            idle = yield from cursor.fetchone()
            if idle:
                fid = idle[0]
            else:
                yield from cursor.execute('''
                    INSERT INTO feed VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ''',(None,uid,post,0,"","","","","",0,0))
                yield from connect.commit()
                yield from cursor.execute('''SELECT LAST_INSERT_ID()''')
                last_insert = yield from cursor.fetchone()
                fid = last_insert[0]
                yield from cursor.execute('''
                    INSERT INTO article VALUES(%s,%s)
                ''',(fid,""))
                yield from connect.commit()
                yield from cursor.close()
                connect.close()
            
        except Exception as error:
            if error.args[1].find("user") != -1:
                yield from cursor.close()
                connect.close()
                return web.HTTPForbidden()

        return web.Response(
            text = toolbox.jsonify({"fid": str(fid).zfill(8)}),
            headers = {'Access-Control-Allow-Origin':'*'},
            content_type='application/json',
            charset='utf-8'
        )
