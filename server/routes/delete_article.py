import asyncio
import re, datetime
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

    query_parameters = request.rel_url.query
    if "fid" in query_parameters:
        try:
            fid = int(query_parameters["fid"])
        except:
            return web.HTTPBadRequest()


    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()

        result = yield from cursor.execute('''
            UPDATE feed SET 
            status = 0
            WHERE id = %s and uid = %s;
        ''',(fid,uid))
        yield from connect.commit()

        yield from cursor.close()
        connect.close()

        if result:
        	return web.Response()
        else:
        	return web.HTTPForbidden()