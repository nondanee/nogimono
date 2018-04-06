import asyncio
from . import toolbox
from aiohttp import web
from aiohttp_session import get_session

@asyncio.coroutine
def feed(request):

    session = yield from get_session(request)
    if 'uid' in session:
        uid = session['uid']
    else:
        return web.HTTPForbidden()

    page = 1
    offset = 0
    size = 10

    query_parameters = request.rel_url.query
    if "page" in query_parameters:
        try:
            page = int(query_parameters["page"])
            if page == 0:
                return web.HTTPBadRequest()
            offset = (page - 1) * size
        except:
            return web.HTTPBadRequest()

    with (yield from request.app['pool']) as connect:

        cursor= yield from connect.cursor()

        yield from cursor.execute('''
            select
            id,
            post,
            title,
            subtitle,
            snippet
            from feed
            where uid = %s and status = 1
            order by post desc
            limit %s,%s
        ''',(uid,offset,size))

        out = yield from cursor.fetchall()
        yield from cursor.close()
        connect.close()
        
        json_back = []

        for entry in out:
            
            article = {
                "id": str(entry[0]).zfill(8),
                "post": toolbox.time_utc(entry[1]),
                "title": entry[2],
                "subtitle": entry[3],
                "snippet": entry[4],
            }

            json_back.append(article)

        return web.Response(
            text=toolbox.jsonify(json_back),
            content_type="application/json",
            headers={'Access-Control-Allow-Origin':'*'},
            charset="utf-8"
        )


@asyncio.coroutine
def detail(request):

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

        cursor= yield from connect.cursor()

        yield from cursor.execute('''
            select
            feed.id,
            feed.type,
            feed.title,
            feed.subtitle,
            article.text
            from feed
            join article on article.id = feed.id
            where feed.id = %s and feed.uid = %s and feed.status = 1
        ''',(fid,uid))

        out = yield from cursor.fetchall()
        yield from cursor.close()
        connect.close()

        if len(out) == 0:
            return web.HTTPNotFound()

        json_back = {
            "id": str(out[0][0]).zfill(8),
            "type": out[0][1],
            "title": out[0][2],
            "subtitle": out[0][3],
            "article": out[0][4],
        }

        return web.Response(
            text=toolbox.jsonify(json_back),
            content_type="application/json",
            headers={'Access-Control-Allow-Origin':'*'},
            charset="utf-8"
        )
