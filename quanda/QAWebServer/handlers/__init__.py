# coding:utf-8
"""
quanda WebServer Handlers
统一管理所有 API Handler
"""

from quanda.QAWebServer.handlers.datahandler import (
    QAFutureListHandler,
    QAFutureDayHandler,
    QAFutureMinHandler,
    QAFutureRealtimeHandler
)

__all__ = [
    'QAFutureListHandler',
    'QAFutureDayHandler',
    'QAFutureMinHandler',
    'QAFutureRealtimeHandler'
]
