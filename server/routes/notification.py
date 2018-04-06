import asyncio
import os, datetime
from . import toolbox
from aiohttp import web
from aiohttp_session import get_session

@asyncio.coroutine
def route(request):

    page = 1
    size = 10

    query_parameters = request.rel_url.query

    if "page" in query_parameters:
        try:
            page = int(query_parameters["page"])
            page = page if page > 0 else 1
        except:
            return web.HTTPBadRequest()


    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()
        permit = yield from toolbox.headers_access(cursor,request.headers)

        if not permit:
            yield from cursor.close()
            connect.close()
            return toolbox.javaify(401,"unauthorized")
        uid = int(request.headers["uid"])


        yield from cursor.execute('''
            SELECT
            cut.cid,
            cut.uid,
            cut.fid,
            cut.rid,
            cut.root,
            cut.floor,
            cut.post,
            cut.message,
            cut.unread,
            cut.nickname,
            cut.avatar,
            commentx.floor,
            commentx.post,
            commentx.message
            FROM (
                SELECT
                commentx.cid,
                commentx.uid,
                commentx.fid,
                commentx.rid,
                commentx.root,
                commentx.floor,
                commentx.post,
                commentx.message,
                commentx.unread,
                user.nickname,
                user.avatar
                FROM commentx
                JOIN user ON user.id = commentx.uid
                WHERE commentx.rid in (
                    SELECT
                    cid
                    FROM commentx
                    WHERE uid = %s
                    AND status = 1
                )
                AND commentx.status = 1
                ORDER BY commentx.cid DESC 
                LIMIT %s,%s
            )cut
            JOIN commentx ON commentx.cid = cut.rid
            ORDER BY cid DESC
            ''',(uid,(page-1)*size,size))

        replies = yield from cursor.fetchall()
        yield from cursor.close()
        connect.close()

        notifications = []

        for reply in replies:
            notifications.append({
                "id": reply[0],
                "fid": reply[2],
                "post": toolbox.time_stamp(reply[6]),
                "floor": reply[5],
                "root": reply[4],
                "author":{
                    "id": reply[1],
                    "nickname": reply[9],
                    "avatar": reply[10]
                },
                "origin":{
                    "id": reply[3],
                    "post": toolbox.time_stamp(reply[12]),
                    "floor": reply[11],
                    "message": reply[13],
                },
                "message": reply[7],
                "unread": bool(reply[8]),
            })

        return toolbox.javaify(200,"ok",notifications)
