import os

import asyncio
import requests

from aiohttp import web

from api.utilies import fileworker as fw

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

    async def post_excel(self, request):
        reader = await request.multipart()

        field = await reader.next()

        size = 0
        with open(os.path.join('./api/tmp/data/', 'loaded.xlsx'), 'wb+') as f:
            while True:
                chunk = await field.read_chunk()  # 8192 bytes by default.
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

        #web.Response(text='Excel-report sized of {0} successfully stored'.format(size))
        return web.FileResponse(path='./api/tmp/data/loaded.xlsx', status=200) 

    async def post_jpg(self, request):
        reader = await request.multipart()

        field = await reader.next()

        size = 0
        with open(os.path.join('./api/tmp/data/', 'loaded.jpg'), 'wb+') as f:
            while True:
                chunk = await field.read_chunk()  # 8192 bytes by default.
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

        #web.Response(text='Excel-report sized of {0} successfully stored'.format(size))
        return web.FileResponse(path='./api/tmp/data/loaded.jpg', status=200) 

    async def post_links(self, request):
        reader = await request.json()

        link1 = reader['file1']
        link2 = reader['file2']

        r1 = requests.get(link1)
        r2 = requests.get(link2)

        with open("../api/tmp/cashes/reports/АПВО.xlsx", "wb") as file:
            file.write(r1.content)
        
        with open("../api/tmp/cashes/reports/ССПС.xlsx", "wb") as file:
            file.write(r2.content)

        worker = fw.Worker('../api/tmp/cashes/reports')

        worker.read_files()
        worker.make_dataset()
        worker.make_report()
        worker.save_report('out_report.xlsx')

        return web.FileResponse(path='../api/tmp/cashes/reports/out_report.xlsx', status=200) 

    async def get_plot(self, request):
        name = request.match_info.get('name', "Anonymous")

        #web.Response(text='Excel-report sized of {0} successfully stored'.format(size))
        return web.FileResponse(path='./api/tmp/data/plot_exemple.png', status=200) 