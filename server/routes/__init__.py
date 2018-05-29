from . import site_index, user_login, user_home
from . import upload_create, upload_photo, upload_article, delete_article
from . import archive_query, platform_feed, platform_data
from . import user_avatar
from . import comment, reply, notification

def setup_routes(app):

    app.router.add_route("GET", "/", site_index.route)
    app.router.add_route("GET", "/home", user_home.route)

    app.router.add_route("POST", "/user/login", user_login.route)
    app.router.add_route("POST", "/user/avatar", user_avatar.route)

    app.router.add_route("GET", "/archive/feed", archive_query.feed)
    app.router.add_route("GET", "/archive/detail", archive_query.detail)

    app.router.add_route("POST", "/upload/create", upload_create.route)
    app.router.add_route("POST", "/upload/photo", upload_photo.route)
    app.router.add_route("POST", "/upload/article", upload_article.route)
    app.router.add_route("POST", "/delete/article", delete_article.route)


    # app.router.add_route('POST', '/session/clean', clean)
    # app.router.add_route('POST', '/submit/photo', photo_bed)
    # app.router.add_route('POST', '/submit/article', article)
    # app.router.add_route('POST', '/delete/photo', delete_photo)
    # app.router.add_route('GET', '/preview/article/{room:\d{6}}', preview)
    # app.router.add_route('POST', '/delete/article/{room:\d{6}}', delete_article)
    # app.router.add_route('GET', '/mbview/article/{room:\d{6}}', mbview)


    # app.router.add_route('GET', '/api/feed/platform', platform_feed.route)
    app.router.add_route("GET", "/data/list", platform_feed.route)
    app.router.add_route("GET", "/{type:view}/{fid:\d{8}}", platform_data.route)
    app.router.add_route("GET", "/{type:data}/{fid:\d{8}}", platform_data.route)

    # app.router.add_route('GET', '/data/feed/official-blog', blogs)

    # app.router.add_route('GET', '/data/detail/article', oneentry)
    # app.router.add_route('GET', '/data/intro', memberdetail)


    app.router.add_route("POST", "/comment", comment.create)
    app.router.add_route("DELETE", "/comment", comment.delete)
    app.router.add_route("GET", "/comment", comment.query)
    app.router.add_route("POST", "/reply", reply.create)
    app.router.add_route("GET", "/reply", reply.query)

    app.router.add_route("GET", "/notification", notification.route)