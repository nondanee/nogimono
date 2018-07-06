import asyncio
import re
from . import toolbox
from aiohttp import web
from aiohttp_session import get_session
image_picker = re.compile(r'([\d|a-f]{32}\.(jpg|png|gif))')

@asyncio.coroutine
def route(request):

    fid = request.match_info["fid"]

    with (yield from request.app['pool']) as connect:
        cursor = yield from connect.cursor()
        yield from cursor.execute('''
            select
            target.id,
            target.post,
            target.type,
            target.title,
            target.subtitle,
            target.cdn,
            user.nickname,
            article.text,
            article.raw
            from(
                select
                feed.id,
                feed.uid,
                feed.post,
                feed.type,
                feed.title,
                feed.subtitle,
                feed.cdn
                from feed
                where feed.id = %s
                and feed.status = 1
            ) target
            join user on user.id = target.uid
            join article on article.id = target.id
        ''',(fid,))
        out = yield from cursor.fetchone()
        yield from cursor.close()
        connect.close()

    if not out: return web.HTTPNotFound()

    post = toolbox.time_stamp(out[1])
    category = toolbox.number_to_type(out[2])
    title = out[3]
    subtitle = out[4]
    cdn = out[5]
    provider = out[6]
    article = out[7]
    raw = out[8] if out[8] else ''

    if cdn == 1:
        article = image_picker.sub('http://{}/{}/\g<1>'.format(request.app["qiniu_domain"],fid),article)
        raw = image_picker.sub('http://{}/{}/\g<1>'.format(request.app["qiniu_domain"],fid),raw)
    elif cdn == 0:
        article = image_picker.sub('/photo/{}/\g<1>'.format(fid),article)
        raw = image_picker.sub('/photo/{}/\g<1>'.format(fid),raw)
    elif cdn == -1:
        article = image_picker.sub('/temp/{}/\g<1>'.format(fid),article)
        raw = image_picker.sub('/temp/{}/\g<1>'.format(fid),raw)

    json_back = {
        "fid": fid,
        "post": post,
        "type": category,
        "provider": provider,
        "title": title,
        "subtitle": subtitle,
        "article": article,
        "raw": raw
    }

    if request.match_info["type"] == "view":

        html_back = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="theme-color" content="#812990">
    <title>乃木物</title>
    <link rel="stylesheet" type="text/css" href="/static/css/view.css"/>
    <script src="/static/js/marked.min.js"></script>
    <script src="/static/js/view.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
</head>
<body>
</body>
<script>var shareData = {}</script>
</html>'''.format(toolbox.jsonify(json_back))

        return web.Response(
            text = html_back,
            content_type = 'text/html',
            charset = 'utf-8'
        )

    else:

        return web.Response(
            text = toolbox.jsonify(json_back),
            content_type = 'application/json',
            charset = 'utf-8'
        )
