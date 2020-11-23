import asyncio

from aiohttp import web

from api.routes import setup_routes

async def init(argv=None):

    app = web.Application()
    
    setup_routes(app)

    return app