import os

import asyncio

from aiohttp import web

class Handler:

    def __init__(self):
        pass

    @asyncio.coroutine
    def hello(self, request):
        name = request.match_info.get('name', "Anonymous")
        txt = "Hello, {}".format(name)
        return web.Response(text=txt)

    @asyncio.coroutine
    def get_json(self, request):
        data = {'hello': 'word'}
        return web.json_response(data)

    async def post_file(self, request):
        data = await request.post()
        file = data['file'] # как словарь
        #print(file) # 
        #print(file.file, file.filename)
        f = file.file # _io.BufferedRandom
        chars = f.read(20)

        return  web.Response(text='Successfully read first 20 chars: {0}'.format(chars))
