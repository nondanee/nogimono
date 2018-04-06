import asyncio
from . import toolbox
from aiohttp import web
from aiohttp_session import get_session

@asyncio.coroutine
def route(request):

    query_parameters = request.rel_url.query

    type_number = 0
    query_condition = ""
    size = 10
    page = 1
    offset = 0

    if "type" in query_parameters:
        type_number = toolbox.type_to_number(query_parameters["type"])
        if type_number == None:
            return web.HTTPBadRequest()
        elif type_number != 0:
            query_condition = "and type = %s"%type_number  

    if "size" in query_parameters:
        try:
            size = int(query_parameters["size"])
            if size > 100:
                return web.HTTPBadRequest()
        except:
            return web.HTTPBadRequest()

    if "page" in query_parameters:
        try:
            page = int(query_parameters["page"])
            if page == 0:
                return web.HTTPBadRequest()
            offset = (page - 1) * size
        except:
            return web.HTTPBadRequest()
    

    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()

        exist = yield from cursor.execute('''
            select
            cut.id,
            cut.post,
            cut.type,
            cut.title,
            cut.subtitle,
            cut.snippet,
            cut.images,
            cut.status,
            user.nickname
            from(
                select
                feed.id,
                feed.uid,
                feed.post,
                feed.type,
                feed.title,
                feed.subtitle,
                feed.snippet,
                feed.images,
                feed.status
                from feed
                where feed.status = 1
                %s
                order by feed.post desc
                limit %s,%s 
            ) cut
            join user on user.id = cut.uid
        '''%(query_condition,offset,size))

        out = yield from cursor.fetchall()
        yield from cursor.close()
        connect.close()

    json_back = []

    for line in out:

        if line[7]:
            prefix = "http://{}".format(request.app["qiniu_domain"])
            suffix = "?imageView2/1/w/250/h/200/q/80"
        else:
            prefix = "https://{}/photo".format(request.app["server_domain"])
            suffix = ""

        images = line[6].split(",")
        if len(images) >= 3:
            images_dealt = []
            for n in range(0,3):
                images_dealt.append({"image":"{}/{}/{}{}".format(prefix,str(line[0]).zfill(8),images[n],suffix)})
        elif len(images) >= 1:
            images_dealt = [{"image":"{}/{}/{}{}".format(prefix,str(line[0]).zfill(8),images[0],suffix)}]
        else:
            images_dealt = None

        #json_back.append({
        #    "id": line[0],
        #    "delivery": toolbox.time_stamp(line[1]),
        #    "type": toolbox.number_to_type(line[2]),
        #    "title": line[3],
        #    "subtitle": line[4],
        #    "snippet": line[5],
        #    "provider": line[7],
        #    "images": images_dealt
        #})

        json_back.append({
            "id": str(line[0]).zfill(8),
            "delivery": toolbox.time_stamp(line[1]),
            "type": toolbox.number_to_type(line[2]),
            "title": line[3],
            "subtitle": line[4],
            "summary": line[5],
            "provider": line[8],
            "view": "/view/{}".format(str(line[0]).zfill(8)),
            "data": "/data/{}".format(str(line[0]).zfill(8)),
            "withpic": images_dealt
        })

    return web.Response(
        text = toolbox.jsonify(json_back),
        content_type = 'application/json',
        charset = 'utf-8'
    )
