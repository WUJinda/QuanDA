# coding:utf-8
"""
quanda WebServer Handlers
统一管理所有 API Handler
"""

# 数据接口
from quanda.QDWebServer.handlers.datahandler import (
    QDFutureListHandler,
    QDFutureDayHandler,
    QDFutureMinHandler,
    QDFutureRealtimeHandler
)

# 策略参考库接口
from quanda.QDWebServer.handlers.strategyreference import (
    StrategyReferenceListHandler,
    StrategyReferenceDetailHandler,
    StrategyReferenceCreateHandler,
    StrategyReferenceUpdateHandler,
    StrategyReferenceDeleteHandler,
    StrategyReferenceUploadHandler,
    StrategyReferenceAnalyzeHandler
)

# 所有数据接口 Handler
DATA_HANDLERS = [
    (r"/future/list", QDFutureListHandler),
    (r"/future/day", QDFutureDayHandler),
    (r"/future/min", QDFutureMinHandler),
    (r"/future/realtime", QDFutureRealtimeHandler),
]

# 所有策略参考库 Handler
STRATEGY_REFERENCE_HANDLERS = [
    (r"/strategy-reference/list", StrategyReferenceListHandler),
    (r"/strategy-reference/analyze", StrategyReferenceAnalyzeHandler),
    (r"/strategy-reference/create", StrategyReferenceCreateHandler),
    (r"/strategy-reference/upload", StrategyReferenceUploadHandler),
    (r"/strategy-reference/update/([^/]+)", StrategyReferenceUpdateHandler),
    (r"/strategy-reference/delete/([^/]+)", StrategyReferenceDeleteHandler),
    (r"/strategy-reference/([^/]+)", StrategyReferenceDetailHandler),
]

# 所有 API 路由
ALL_API_ROUTES = DATA_HANDLERS + STRATEGY_REFERENCE_HANDLERS

__all__ = [
    # Data Handlers
    'QDFutureListHandler',
    'QDFutureDayHandler',
    'QDFutureMinHandler',
    'QDFutureRealtimeHandler',
    # Strategy Reference Handlers
    'StrategyReferenceListHandler',
    'StrategyReferenceDetailHandler',
    'StrategyReferenceCreateHandler',
    'StrategyReferenceUpdateHandler',
    'StrategyReferenceDeleteHandler',
    'StrategyReferenceUploadHandler',
    'StrategyReferenceAnalyzeHandler',
    # Route collections
    'DATA_HANDLERS',
    'STRATEGY_REFERENCE_HANDLERS',
    'ALL_API_ROUTES',
]
