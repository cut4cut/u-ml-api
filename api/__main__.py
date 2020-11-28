import asyncio
import argparse
import logging

from aiohttp import web
from api.routes import setup_routes

parser = argparse.ArgumentParser(description="aiohttp server example")
parser.add_argument('--host')
parser.add_argument('--port')

def main():
        logging.basicConfig(level=logging.DEBUG)
        args = parser.parse_args()
        app = web.Application()
        
        setup_routes(app)

        web.run_app(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()