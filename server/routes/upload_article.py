import asyncio
import re, datetime, os
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
            fid = str(int(query_parameters["fid"])).zfill(8)
        except:
            return web.HTTPBadRequest()
    else:
        return web.HTTPBadRequest()

    if request.content_type != "application/x-www-form-urlencoded":
        return web.HTTPBadRequest()

    data = yield from request.post()

    if 'title' in data:
        title = data['title'] 
    else:
        return web.HTTPBadRequest()
    
    if 'subtitle' in data:
        subtitle = data['subtitle']
    else:
        return web.HTTPBadRequest()

    if 'type' in data:
        try:
            type_number = int(data['type'])
            if toolbox.number_to_type(type_number) == None:
                return web.HTTPBadRequest()
        except:
            return web.HTTPBadRequest()
    else:
        return web.HTTPBadRequest()

    if 'article' in data:
        article = data['article']
        article = re.sub(r'\r\n','\n',article)
    else:
        return web.HTTPBadRequest()

    post = datetime.datetime.now()

    snippet = re.sub(r'http://',"", article)
    snippet = re.sub(r'https://',"", snippet)
    snippet = re.sub(r'\!\[[^\]]*\]\([^\)]+?\)',"",snippet)
    snippet = re.sub(r'\s+'," ",snippet)
    snippet = re.sub(r'^\s+',"",snippet)
    snippet = snippet[0:80]
    snippet = re.sub(r'\s$',"",snippet)
    if len(snippet) == 80: snippet = snippet+"..."

    images_raw = re.findall(r'([\d|a-f]{32}\.(jpg|png|gif))',article)
    images_raw = [image[0] for image in images_raw]
    images = list(set(images_raw))
    images.sort(key=images_raw.index)

    with (yield from request.app['pool']) as connect:

        cursor = yield from connect.cursor()

        yield from cursor.execute('''SELECT post,type FROM feed WHERE id = %s AND uid = %s AND status <> 0''',(fid,uid))
        check = yield from cursor.fetchone()        

        try:
            if not check:
                return web.HTTPForbidden()
            elif check[1] == 0:
                yield from cursor.execute('''
                    UPDATE feed SET 
                    post = %s, 
                    type = %s, 
                    title = %s, 
                    subtitle = %s, 
                    snippet = %s, 
                    images = %s,
                    status = 1
                    WHERE id = %s;
                ''',(post.strftime("%Y/%m/%d %H:%M"),type_number,title,subtitle,snippet,",".join(images),fid))

            else:
                post = check[0]
                yield from cursor.execute('''
                    UPDATE feed SET 
                    type = %s, 
                    title = %s, 
                    subtitle = %s, 
                    snippet = %s, 
                    images = %s,
                    status = 1
                    WHERE id = %s;
                ''',(type_number,title,subtitle,snippet,",".join(images),fid))

            yield from connect.commit()

            yield from cursor.execute('''
                UPDATE article SET 
                text = %s
                WHERE id = %s;
            ''',(article,fid))
            yield from connect.commit()

        except Exception as e:
            print(e)
            return web.HTTPBadRequest()

        yield from cursor.close()
        connect.close()


    os.system("python3 {working_dir}/server/transmit.py {fid} &".format(
        working_dir = request.app["working_dir"],
        fid = fid
    ))

    return web.Response(
        text = toolbox.jsonify({
            "id": str(fid).zfill(8),
            "post": toolbox.time_utc(post),
            "title": title,
            "subtitle": subtitle,
            "snippet": snippet,
        }),
        headers = {'Access-Control-Allow-Origin':'*'},
        content_type='application/json',
        charset='utf-8'
    )
