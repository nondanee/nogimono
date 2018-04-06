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

    if 'fid' in data:
        try:
            fid = int(data["fid"])
        except:
            return toolbox.javaify(400,"fid format error")
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

        yield from cursor.execute('''SELECT floor FROM commentx WHERE fid = %s AND root = 0 ORDER BY cid DESC LIMIT 1''',(fid))
        floor_previous = yield from cursor.fetchone()
        floor = int(floor_previous[0]) + 1 if floor_previous else 1

        try:
            yield from cursor.execute('''
                INSERT INTO commentx VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ''',(None,uid,fid,0,0,floor,post.strftime("%Y/%m/%d %H:%M:%S"),message,0,1))
            yield from connect.commit()

        except Exception as error:
            print(error)
            if error.args[1].find("user") != -1:
                yield from cursor.close()
                connect.close()
                return toolbox.javaify(400,"bad request")
            elif error.args[1].find("feed") != -1:
                yield from cursor.close()
                connect.close()
                return toolbox.javaify(400,"bad request")
        else:
            yield from cursor.close()
            connect.close()
            return toolbox.javaify(200,"success")


@asyncio.coroutine
def delete(request):

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
            return toolbox.javaify(400,"fid format error")
    else:
        return toolbox.javaify(400,"miss argument")

    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()

        # permit = yield from toolbox.access(cursor,uid,token)
        permit = yield from toolbox.headers_access(cursor,request.headers)

        if not permit:
            yield from cursor.close()
            connect.close()
            return toolbox.javaify(401,"unauthorized")
        uid = int(request.headers["uid"])

        yield from cursor.execute('''SELECT root FROM commentx WHERE cid = %s and uid = %s AND status = 1''',(cid,uid))
        target = yield from cursor.fetchone()
        if not target:
            return toolbox.javaify(400,"bad request")
        elif target[0] == 0:
            yield from cursor.execute('''UPDATE commentx SET status = 0 WHERE root = %s OR cid = %s''',(cid,cid))
            yield from connect.commit()
        else:
            cids = set([cid])
            while True:
                yield from cursor.execute('''SELECT cid FROM commentx WHERE rid IN (%s)'''%(','.join(map(lambda x:'%s',cids))),tuple(cids))
                get = yield from cursor.fetchall()
                refresh = set([one[0] for one in get])|cids
                if refresh == cids:
                    break
                cids = refresh
            yield from cursor.executemany('''UPDATE commentx SET status = 0 WHERE cid = %s''',tuple(cids))
            yield from connect.commit()

        yield from cursor.close()
        connect.close()

        return toolbox.javaify(200,"success")



@asyncio.coroutine
def query(request):

    page = 1
    size = 10

    query_parameters = request.rel_url.query

    if "fid" in query_parameters:
        try:
            fid = int(query_parameters["fid"])
        except:
            return toolbox.javaify(400,"fid format error")
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
            cut.cid,
            cut.uid,
            cut.floor,
            cut.post,
            cut.message,
            user.nickname,
            user.avatar
            FROM(
                SELECT 
                cid,
                uid,
                floor,
                post,
                message
                FROM commentx 
                WHERE fid = %s 
                AND root = 0
                AND status = 1
                ORDER BY cid DESC
                LIMIT %s,%s
            )cut
            JOIN user ON user.id = cut.uid
        ''',(fid,(page-1)*size,size))
        comments = yield from cursor.fetchall()

        cids = []
        json_back = []

        for comment in comments:
            cids.append(comment[0])
            json_back.append({
                "id": comment[0],
                "post": toolbox.time_stamp(comment[3]),
                "floor": comment[2],
                "message": comment[4],
                "author":{
                    "id": comment[1],
                    "nickname": comment[5],
                    "avatar": comment[6]
                },
                "children": None
            })

        readed_cids = []

        for index,cid in enumerate(cids):
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
                        FROM (
                            SELECT
                            cid,
                            uid,
                            rid,
                            floor,
                            post,
                            message
                            FROM commentx
                            WHERE commentx.root = %s
                            AND status = 1
                            ORDER BY cid DESC
                            LIMIT 3
                        )cut
                        LEFT JOIN commentx ON commentx.cid = cut.rid
                    )deal
                    JOIN user ON user.id = deal.to_uid
                )final
                JOIN user ON user.id = final.uid
            ''',(cid))
        
            replies = yield from cursor.fetchall()
            children = []
            
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

            json_back[index]["children"] = children

        yield from cursor.executemany('''UPDATE commentx SET unread = 0 WHERE cid = %s''',readed_cids)
        yield from connect.commit()
        yield from cursor.close()
        connect.close()

        return toolbox.javaify(200,"ok",json_back)

        # if cids == []:
        #     return toolbox.javaify(200,json_back,"ok")

        # yield from cursor.execute('''
        #     SELECT
        #     final.cid,
        #     final.uid,
        #     final.rid,
        #     final.root,
        #     final.floor,
        #     final.post,
        #     final.message,
        #     final.to_uid,
        #     final.to_nickname,
        #     user.nickname,
        #     user.avatar
        #     FROM(
        #         SELECT
        #         deal.cid,
        #         deal.uid,
        #         deal.rid,
        #         deal.root,
        #         deal.floor,
        #         deal.post,
        #         deal.message,
        #         deal.to_uid,
        #         user.nickname AS to_nickname
        #         FROM(
        #             SELECT
        #             cut.cid,
        #             cut.uid,
        #             cut.rid,
        #             cut.root,
        #             cut.floor,
        #             cut.post,
        #             cut.message,
        #             commentx.uid AS to_uid
        #             FROM (
        #                 SELECT
        #                 cid,
        #                 uid,
        #                 rid,
        #                 root,
        #                 floor,
        #                 post,
        #                 message
        #                 FROM commentx
        #                 WHERE commentx.root IN (%s)
        #                 AND status = 1 
        #             )cut
        #             LEFT JOIN commentx ON commentx.cid = cut.rid
        #         )deal
        #         JOIN user ON user.id = deal.to_uid
        #     )final
        #     JOIN user ON user.id = final.uid
        #     ORDER BY final.cid DESC
        # '''%(','.join(map(lambda x: '%s', cids))),(cids))

        # # AND floor <= 5
        # # ORDER BY cid ASC
        # # ORDER BY final.cid DESC
        
        # replies = yield from cursor.fetchall()

        # for reply in replies:

        #     index = cids.index(reply[3])
        #     if not json_back[index]["children"]:
        #         json_back[index]["children"] = []

        #     json_back[index]["children"].append({
        #         "id": reply[0],
        #         "post": toolbox.time_stamp(reply[5]),
        #         "floor": reply[4],
        #         "author":{
        #             "id": reply[1],
        #             "nickname": reply[9],
        #             "avatar": reply[10]
        #         },
        #         "message": reply[6] if reply[3] == reply[2] else "回复 @{} :{}".format(reply[8],reply[6]),
        #     })

        # return toolbox.javaify(200,"ok",json_back)