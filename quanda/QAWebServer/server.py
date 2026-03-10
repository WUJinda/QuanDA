# coding:utf-8
#
# The MIT License (MIT)
#
import asyncio
import os
import sys

import tornado
from quanda import __version__
from quanda.QAUtil.QASetting import QASETTING
from quanda.QAWebServer.basehandles import QABaseHandler
from quanda.QAWebServer.commandhandler import (CommandHandler,
                                                  CommandHandlerWS,
                                                  RunnerHandler)
from quanda.QAWebServer.schedulehandler import (QAScheduleQuery,
                                                   QASchedulerHandler,
                                                   init_scheduler)
from quanda.QAWebServer.qifiserver import QAQIFI_Handler, QAQIFIS_Handler, QAQIFIS_REALTIME_Handler
from quanda.QAWebServer.handlers import ALL_API_ROUTES
from tornado.options import (define, options, parse_command_line,
                             parse_config_file)
from tornado.web import Application, RequestHandler, authenticated


class INDEX(QABaseHandler):

    def get(self):
        self.write(
            {
                'status': 200,
                'message': 'This is a welcome page for quanda backend',
                'url': [item[0] for item in handlers]
            }
        )


class QAUserhander(QABaseHandler):
    def get(self):
        self.write({'status': 200, 'result':{'user_cookie': 'xx'}})

#term_manager = SingleTermManager(shell_command=['bash'])
handlers = [
    (r"/", INDEX),
    (r"/command/run", CommandHandler),
    (r"/command/runws", CommandHandlerWS),
    (r"/command/runbacktest", RunnerHandler),
    (r"/scheduler/map/?", QASchedulerHandler),
    (r"/scheduler/query", QAScheduleQuery),
    (r"/qifi", QAQIFI_Handler),
    (r"/qifis", QAQIFIS_Handler),
    (r"/qifirealtime", QAQIFIS_REALTIME_Handler),
    (r"/user", QAUserhander),
] + ALL_API_ROUTES


def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    define("port", default=8010, type=int, help="服务器监听端口号")

    define("address", default='0.0.0.0', type=str, help='服务器地址')
    define("content", default=[], type=str, multiple=True, help="控制台输出内容")

    parse_command_line()
    port = options.port
    address = options.address
    scheduler = init_scheduler()

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
    
    print('========WELCOME quanda_WEBSERVER 2.0 ============')
    print('quanda VERSION: {}'.format(__version__))
    print('quanda WEBSERVER is Listening on: http://{}:{}'.format(address, port))
    print('Static files path: {}'.format(static_path))
    print('请打开浏览器/使用JavaScript等来使用该后台, 并且不要关闭当前命令行窗口')
    apps.listen(port, address=address)

    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
