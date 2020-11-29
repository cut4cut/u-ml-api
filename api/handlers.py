import os

import asyncio
import requests

import pandas as pd

from aiohttp import web
from pathlib import Path

from api.utilies import plotstats as ps
from api.utilies import fileworker as fw

from api.utilies.fileworker import get_raiting_

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

        with open("./api/tmp/cashes/reports/АПВО.xlsx", "wb") as file:
            file.write(r1.content)
        
        with open("./api/tmp/cashes/reports/ССПС.xlsx", "wb") as file:
            file.write(r2.content)

        worker = fw.Worker('./api/tmp/cashes/reports')

        worker.read_files()
        worker.make_dataset()
        worker.make_report()
        worker.save_report('out_report.xlsx')

        return web.FileResponse(path='./api/tmp/cashes/reports/out_report.xlsx', status=200) 

    async def get_raiting(self, request):
        params = request.match_info.get('params', 'Anonymous')
        arr = params.split('|')
        dataset = pd.read_csv('./api/tmp/cashes/data/dataset.csv')
        
        column = arr[0]
        month = arr[1]
        print(params)
        raiting_json = get_raiting_(dataset, month, column)

        return web.json_response(raiting_json)

    async def get_plot(self, request):
        main_path = './api/tmp/cashes/plots/{0}'
        fig_name = request.match_info.get('name', 'Anonymous')

        fig_path = main_path.format(fig_name) + '.png'
        fig_file = Path(fig_path)
        #print(fig_file)
        if fig_file.is_file():
            return web.FileResponse(path=fig_path, status=200)
        else:
            name_date = fig_name.split('_')
            machine_type = name_date[0]
            date = name_date[1]
            data = pd.read_csv('./api/tmp/cashes/data/data_m.csv')
            ps.plot_rate_fact(data, machine_type, date, fig_path=main_path)

            return web.FileResponse(path=fig_path, status=200) 


        #web.Response(text='Excel-report sized of {0} successfully stored'.format(size))


    async def get_model(self, request):
        main_path = './api/tmp/cashes/models/{0}'
        fig_name = request.match_info.get('name', 'Anonymous')

        fig_path = main_path.format(fig_name) + '.png'
        fig_file = Path(fig_path)
        #print(fig_file)
        if fig_file.is_file():
            return web.FileResponse(path=fig_path, status=200)
        else:
            return web.Response(text='Извините, модель на обучении ;-)')

    
        