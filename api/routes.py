from aiohttp import web

from api.handlers import Handler

def setup_routes(app):
    handler = Handler()

    app.router.add_routes([
        web.get("/hello/{name}", handler.hello),
        web.get("/get/json", handler.get_json),
        web.get("/get/plot/{name}", handler.get_plot),
        web.get("/get/raiting/{params}", handler.get_raiting),
        web.post("/post/excel", handler.post_excel),
        web.post("/post/jpg", handler.post_jpg),
        web.post("/post/links", handler.post_links)
    ])