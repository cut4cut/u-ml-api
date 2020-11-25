from aiohttp import web

from api.handlers import Handler

def setup_routes(app):
    handler = Handler()

    app.router.add_routes([
        web.get("/hello/{name}", handler.hello),
        web.get("/get/json", handler.get_json),
        web.post("/post/excel", handler.post_excel),
        web.post("/post/jpg", handler.post_jpg)
    ])