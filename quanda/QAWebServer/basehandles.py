# coding:utf-8
#
# The MIT License (MIT)
#
import inspect
import json
import re
import sys
import xml.dom.minidom

import tornado
import tornado.ioloop
import tornado.web
import tornado.wsgi
from quanda.QAWebServer.util import (APPLICATION_JSON, APPLICATION_XML,
                                        TEXT_XML, convert)
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

"""
基础类
"""


class QABaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def set_default_headers(self):


        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header("Access-Control-Allow-Origin", "*")  # 这个地方可以写域名
        #self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods',
                        'POST, GET, OPTIONS, DELETE, PUT, PATCH')
        self.set_header('Access-Control-Allow-Headers',
                        "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, XMLHttpRequest,HTTP2-Settings")
        self.set_header(
            'Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        self.set_header('Server', 'quandaBACKEND')
        #headers.set('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
        # self.Content-Type: text/html; charset=utf-8

    def post(self, *args, **kwargs):
        self.write('some post')

    def get(self, *args, **kwargs):
        self.write('some get')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    def wirte_error(self, status_code, **kwargs):
        pass

    def initialize(self):
        pass

    def on_finish(self):
        pass


class QAWebSocketHandler(WebSocketHandler):

    def check_origin(self, origin):
        return True

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods',
                        'POST, GET, OPTIONS, DELETE, PUT, PATCH')
        self.set_header('Access-Control-Max-Age',
                        999999999999999999999999999999999)
        self.set_header('Access-Control-Allow-Headers',
                        "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With,HTTP2-Settings")
        self.set_header('Server', 'quandaBACKEND')

    def open(self,  *args, **kwargs):
        self.write_message('x')
