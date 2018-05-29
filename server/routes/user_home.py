import asyncio
from aiohttp import web
from aiohttp_session import get_session


html = '''
<!DOCTYPE html>
<html>
<head>
	<title>乃木物</title>
	<meta charset="utf-8">
	<link rel="stylesheet" href="/static/css/simplemde.min.css">
	<link rel="stylesheet" href="/static/css/home.css">
	<script src="/static/js/simplemde.min.js"></script>
	<script src="/static/js/inline-attachment.min.js"></script>
	<script src="/static/js/codemirror-4.inline-attachment.min.js"></script>
	<script src="/static/js/marked.min.js"></script>
</head>
<body>
<container>
	<div id="side-box">
        <button id="create">新建文章</button>
		<div id="feed"></div>
	</div>
	<div id="input-box">
		<input id="title" placeholder="标题"></input>
		<div class="line">
			<input id="subtitle" placeholder="副标题"></input>
			<select id="type">
				<option value ="1">博客</option>
				<option value ="2">杂志</option>
				<option value="3">新闻</option>
			</select>
		</div>
		<textarea id="article"></textarea>
		<button id="submit">提交</button>
	</div>
</container>
</body>
<script src="/static/js/home.js"></script>
</html>
'''


@asyncio.coroutine
def route(request):

    session = yield from get_session(request)
    if 'uid' not in session:
        return web.HTTPFound('/')
    else:
        session["uid"] = session["uid"]
        return web.Response(
            text = html,
            content_type = 'text/html',
            charset = 'utf-8'
        )
