import asyncio
import os, datetime
from . import toolbox
from aiohttp import web
from aiohttp_session import get_session

@asyncio.coroutine
def create(request):

    if request.content_type != "application/x-www-form-urlencoded":
        return toolbox.javaify(400,"content type error")

    data = yield from request.post()

    # if 'uid' in data:
    #     try:
    #         uid = str(int(data["uid"])).zfill(8)
    #     except:
    #         return toolbox.javaify(400,"uid format error")
    # else:
    #     return toolbox.javaify(400,"miss argument")
    
    # if 'token' in data:
    #     token = data['token']
    # else:
    #     return toolbox.javaify(400,"miss argument")

    if 'cid' in data:
        try:
            cid = int(data["cid"])
        except:
            return toolbox.javaify(400,"cid format error")
    else:
        return toolbox.javaify(400,"miss argument")

    if 'message' in data:
        message = data['message']
    else:
        return toolbox.javaify(400,"miss argument")

    post = datetime.datetime.now()

    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()

        # permit = yield from toolbox.access(cursor,uid,token)
        permit = yield from toolbox.headers_access(cursor,request.headers)

        if not permit:
            yield from cursor.close()
            connect.close()
            return toolbox.javaify(401,"unauthorized")
        uid = int(request.headers["uid"])

        yield from cursor.execute('''SELECT fid,root FROM commentx WHERE cid = %s''',(cid))
        origin = yield from cursor.fetchone()
        if not origin:
            yield from cursor.close()
            connect.close()
            return toolbox.javaify(400,"bad request")
        fid = origin[0]
        root = cid if origin[1] == 0 else origin[1]

        yield from cursor.execute('''SELECT floor FROM commentx WHERE root = %s ORDER BY cid DESC LIMIT 1''',(root))
        floor_previous = yield from cursor.fetchone()
        floor = int(floor_previous[0]) + 1 if floor_previous else 1

        try:
            yield from cursor.execute('''
                INSERT INTO commentx VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ''',(None,uid,fid,cid,root,floor,post.strftime("%Y/%m/%d %H:%M:%S"),message,1,1))
            yield from connect.commit()

        except Exception as error:
            print(error)
            if error.args[1].find("user") != -1:
                yield from cursor.close()
                connect.close()
                return toolbox.javaify(400,"bad request")
        else:
            yield from cursor.close()
            connect.close()
            return toolbox.javaify(200,"success")


@asyncio.coroutine
def query(request):

    page = 1
    size = 10

    query_parameters = request.rel_url.query

    if "cid" in query_parameters:
        try:
            cid = int(query_parameters["cid"])
        except:
            return toolbox.javaify(400,"cid format error")
    else:
        return toolbox.javaify(400,"miss argument")

    if "page" in query_parameters:
        try:
            page = int(query_parameters["page"])
            page = page if page > 0 else 1
        except:
            return toolbox.javaify(400,"page format error")


    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()

        permit = yield from toolbox.headers_access(cursor,request.headers)
        if permit:
            uid = int(request.headers["uid"])
        else:
            uid = None

        yield from cursor.execute('''
            SELECT 
            target.cid,
            target.uid,
            target.root,
            target.floor,
            target.post,
            target.message,
            target.status,
            user.nickname,
            user.avatar
            FROM (
                SELECT 
                cid,
                uid,
                root,
                floor,
                post,
                message,
                status
                FROM commentx WHERE cid = %s
            )target
            JOIN user ON user.id = target.uid
        ''',(cid))

        origin = yield from cursor.fetchone()
        if not origin:
            return toolbox.javaify(400,"bad request")
        elif origin[2] != 0 or origin[6] != 1:
            return toolbox.javaify(400,"bad request")
        
        json_back = {
            "id": cid,
            "post": toolbox.time_stamp(origin[4]),
            "floor": origin[3],
            "message": origin[5],
            "author":{
                "id": origin[1],
                "nickname": origin[7],
                "avatar": origin[8]
            },
            "children": None
        }

        yield from cursor.execute('''
            SELECT
            final.cid,
            final.uid,
            final.rid,
            final.floor,
            final.post,
            final.message,
            final.to_uid,
            final.to_nickname,
            user.nickname,
            user.avatar
            FROM(
                SELECT
                deal.cid,
                deal.uid,
                deal.rid,
                deal.floor,
                deal.post,
                deal.message,
                deal.to_uid,
                user.nickname AS to_nickname
                FROM(
                    SELECT
                    cut.cid,
                    cut.uid,
                    cut.rid,
                    cut.floor,
                    cut.post,
                    cut.message,
                    commentx.uid AS to_uid
                    FROM(
                        SELECT 
                        cid,
                        uid,
                        rid,
                        floor,
                        post,
                        message
                        FROM commentx 
                        WHERE root = %s
                        AND status = 1
                        ORDER BY post DESC
                        LIMIT %s,%s
                    )cut
                    LEFT JOIN commentx ON commentx.cid = cut.rid
                )deal
                JOIN user ON user.id = deal.to_uid
            )final
            JOIN user ON user.id = final.uid
        ''',(cid,(page-1)*size,size))
        
        replies = yield from cursor.fetchall()
        children = []
        readed_cids = []

        for reply in replies:

            if uid == reply[1]:
                readed_cids.append(reply[0])

            children.append({
                "id": reply[0],
                "post": toolbox.time_stamp(reply[4]),
                "floor": reply[3],
                "author":{
                    "id": reply[1],
                    "nickname": reply[8],
                    "avatar": reply[9]
                },
                "message": reply[5] if cid == reply[2] else "回复 @{} :{}".format(reply[7],reply[5]),
            })

        json_back["children"] = children

        yield from cursor.executemany('''UPDATE commentx SET unread = 0 WHERE cid = %s''',readed_cids)
        yield from connect.commit()
        yield from cursor.close()
        connect.close()

        return toolbox.javaify(200,"ok",json_back)