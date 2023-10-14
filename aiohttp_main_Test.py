from aiohttp import web

from handlers.main_http_handler import AioMainHTTPHandler

handler = AioMainHTTPHandler()

handler.run()