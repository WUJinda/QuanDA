# coding:utf-8
#
# The MIT License (MIT)
#
import asyncio
import os
import sys

import tornado
from quanda import __version__
from quanda.QDUtil.QDSetting import QASETTING
from quanda.QDWebServer.basehandles import QDBaseHandler
from quanda.QDWebServer.commandhandler import (CommandHandler,
                                                  CommandHandlerWS,
                                                  RunnerHandler)
from quanda.QDWebServer.qifiserver import QDQIFI_Handler, QDQIFIS_Handler, QDQIFIS_REALTIME_Handler
from quanda.QDWebServer.handlers import ALL_API_ROUTES
from tornado.options import (define, options, parse_command_line,
                             parse_config_file)
from tornado.web import Application, RequestHandler, authenticated


class QDIndex(QDBaseHandler):

    def get(self):
        self.write(
            {
                'status': 200,
                'message': 'This is a welcome page for QD backend',
                'url': [item[0] for item in handlers]
            }
        )


class QDUserHandler(QDBaseHandler):
    def get(self):
        self.write({'status': 200, 'result':{'user_cookie': 'xx'}})

handlers = [
    (r"/", QDIndex),
    (r"/command/run", CommandHandler),
    (r"/command/runws", CommandHandlerWS),
    (r"/command/runbacktest", RunnerHandler),
    (r"/qifi", QDQIFI_Handler),
    (r"/qifis", QDQIFIS_Handler),
    (r"/qifirealtime", QDQIFIS_REALTIME_Handler),
    (r"/user", QDUserHandler),
] + ALL_API_ROUTES


def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    define("port", default=8010, type=int, help="服务器监听端口号")

    define("address", default='0.0.0.0', type=str, help='服务器地址')
    define("content", default=[], type=str, multiple=True, help="控制台输出内容")

    parse_command_line()
    port = options.port
    address = options.address

    start_server(handlers, address, port)


def start_server(handlers, address='0.0.0.0', port=8010):
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 配置静态文件路径
    from quanda.config.upload_config import get_upload_path
    upload_root = get_upload_path()
    static_path = os.path.join(project_root, upload_root)
    
    # 确保上传目录存在
    os.makedirs(static_path, exist_ok=True)
    
    apps = Application(
        handlers=handlers,
        debug=True,
        autoreload=True,
        compress_response=True,
        static_path=static_path,
        static_url_prefix='/uploads/'
    )
    
    print('========WELCOME QD WEBSERVER 2.0 ============')
    print('QD VERSION: {}'.format(__version__))
    print('QD WEBSERVER is Listening on: http://{}:{}'.format(address, port))
    print('Static files path: {}'.format(static_path))
    apps.listen(port, address=address)

    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
