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

# 策略管理接口
from quanda.QDWebServer.handlers.strategyhandler import (
    StrategyListHandler,
    StrategyDetailHandler,
    StrategyCreateHandler,
    StrategyUpdateHandler,
    StrategyDeleteHandler,
    StrategyStartHandler,
    StrategyStopHandler,
    StrategyAnalyzeHandler,
    StrategyCodeHandler
)

# 回测系统接口
from quanda.QDWebServer.handlers.backtesthandler import (
    BacktestListHandler,
    BacktestCreateHandler,
    BacktestDetailHandler,
    BacktestResultHandler,
    BacktestRunHandler,
    BacktestDeleteHandler,
    BacktestWebSocketHandler
)

# 所有数据接口 Handler
DATA_HANDLERS = [
    (r"/api/future/list", QDFutureListHandler),
    (r"/api/future/day", QDFutureDayHandler),
    (r"/api/future/min", QDFutureMinHandler),
    (r"/api/future/realtime", QDFutureRealtimeHandler),
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

# 所有策略管理 Handler
STRATEGY_HANDLERS = [
    (r"/api/strategy/list", StrategyListHandler),
    (r"/api/strategy/create", StrategyCreateHandler),
    (r"/api/strategy/analyze", StrategyAnalyzeHandler),
    (r"/api/strategy/([^/]+)/code", StrategyCodeHandler),
    (r"/api/strategy/([^/]+)/start", StrategyStartHandler),
    (r"/api/strategy/([^/]+)/stop", StrategyStopHandler),
    (r"/api/strategy/([^/]+)", StrategyDetailHandler),
]

# 所有回测系统 Handler
BACKTEST_HANDLERS = [
    (r"/api/backtest/list", BacktestListHandler),
    (r"/api/backtest/create", BacktestCreateHandler),
    (r"/api/backtest/run/([^/]+)", BacktestRunHandler),
    (r"/api/backtest/result/([^/]+)", BacktestResultHandler),
    (r"/api/backtest/delete/([^/]+)", BacktestDeleteHandler),
    (r"/api/backtest/([^/]+)", BacktestDetailHandler),
    (r"/api/backtest/ws/([^/]+)", BacktestWebSocketHandler),
]

# 所有 API 路由
ALL_API_ROUTES = DATA_HANDLERS + STRATEGY_REFERENCE_HANDLERS + STRATEGY_HANDLERS + BACKTEST_HANDLERS

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
    # Strategy Handlers
    'StrategyListHandler',
    'StrategyDetailHandler',
    'StrategyCreateHandler',
    'StrategyUpdateHandler',
    'StrategyDeleteHandler',
    'StrategyStartHandler',
    'StrategyStopHandler',
    'StrategyAnalyzeHandler',
    'StrategyCodeHandler',
    # Backtest Handlers
    'BacktestListHandler',
    'BacktestCreateHandler',
    'BacktestDetailHandler',
    'BacktestResultHandler',
    'BacktestRunHandler',
    'BacktestDeleteHandler',
    'BacktestWebSocketHandler',
    # Route collections
    'DATA_HANDLERS',
    'STRATEGY_REFERENCE_HANDLERS',
    'STRATEGY_HANDLERS',
    'BACKTEST_HANDLERS',
    'ALL_API_ROUTES',
]
