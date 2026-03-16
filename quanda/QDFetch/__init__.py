# coding:utf-8
#
# The MIT License (MIT)
#
"""
QAFetch - quanda 数据获取模块

该模块提供统一的金融数据获取接口，支持多种数据源：
- 股票市场：TDX、Tushare、同花顺等
- 期货市场：通达信期货、CTP等
- 数字货币：Binance、Huobi、OKEx等
- 港股美股：通达信、Tushare等

主要功能：
1. 多数据源适配和统一接口
2. 实时行情和历史数据获取
3. 多种数据格式支持(pandas, json, numpy)
4. 数据源切换和容错处理

使用示例：
    # 获取股票日线数据
    data = QA_fetch_get_stock_day('tdx', '000001', '2020-01-01', '2020-12-31')

    # 获取实时行情
    realtime = QA_fetch_get_stock_realtime('tdx', '000001')

@author: yutiansut
@version: 2.0.0
@license: MIT
"""

try:
    from quanda.QDFetch import QATushare as QATushare
except ImportError:
    QATushare = None
try:
    from quanda.QDFetch import QATdx as QATdx
except ImportError:
    QATdx = None
try:
    from quanda.QDFetch import QAThs as QAThs
except ImportError:
    QAThs = None
try:
    from quanda.QDFetch import QACrawler as QACL
except ImportError:
    QACL = None
try:
    from quanda.QDFetch import QAEastMoney as QAEM
except ImportError:
    QAEM = None
try:
    from quanda.QDFetch import QAHexun as QAHexun
except ImportError:
    QAHexun = None
try:
    from quanda.QDFetch import QAfinancial
except ImportError:
    QAfinancial = None
try:
    from quanda.QDFetch.base import get_stock_market
except ImportError:
    get_stock_market = None
try:
    from quanda.QDFetch import QAQAWEB as QAWEB
except ImportError:
    QAWEB = None
try:
    from quanda.QDFetch import QAKQ as QAKQ
except ImportError:
    QAKQ = None
try:
    from quanda.QDFetch import QABaostock as QABaostock
except ImportError:
    QABaostock = None


def use(package):

    if package in ["tushare", "ts"]:
        if QATushare is None:
            raise RuntimeError("tushare 未安装，请运行: pip install tushare")
        return QATushare
    elif package in ["tdx", "pytdx"]:
        if QATdx is None:
            raise RuntimeError("pytdx 未安装，请运行: pip install pytdx")
        return QATdx
    elif package in ["baostock", "bs", "bao"]:
        if QABaostock is None:
            raise RuntimeError("baostock 未安装，请运行: pip install baostock")
        return QABaostock
    elif package in ["ths", "THS"]:
        if QAThs is None:
            raise RuntimeError("lxml 未安装，请运行: pip install lxml")
        return QAThs
    elif package in ["HEXUN", "Hexun", "hexun"]:
        if QAHexun is None:
            raise RuntimeError("hexun 数据源模块不可用")
        return QAHexun
    elif package in ["QA"]:
        if QAWEB is None:
            raise RuntimeError("QA WEB 数据源模块不可用")
        return QAWEB
    else:
        raise RuntimeError(f"不支持的数据源: {package}")


def QA_fetch_get_stock_day(
    package, code, start, end, if_fq="00", level="day", type_="pd"
):
    Engine = use(package)
    if package in ["ths", "THS", "wind"]:
        return Engine.QA_fetch_get_stock_day(code, start, end, if_fq)
    elif package in ["ts", "tushare"]:
        return Engine.QA_fetch_get_stock_day(code, start, end, if_fq, type_)
    elif package in ["baostock", "bs", "bao"]:
        return Engine.QA_fetch_get_stock_day(code, start, end, if_fq, type_)
    elif package in ["tdx", "pytdx"]:
        return Engine.QA_fetch_get_stock_day(code, start, end, if_fq, level)
    else:
        return Engine.QA_fetch_get_stock_day(code, start, end)


def QA_fetch_get_stock_realtime(package, code):
    Engine = use(package)
    return Engine.QA_fetch_get_stock_realtime(code)


def QA_fetch_get_trade_date(package, end, exchange):
    Engine = use(package)
    return Engine.QA_fetch_get_trade_date(end, exchange)


def QA_fetch_get_stock_min(package, code, start, end, level='1min'):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_stock_min(code, start, end, level)
    else:
        return 'Unsupport packages'


def QA_fetch_get_stock_transaction(package, code, start, end, retry=2):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_stock_transaction(code, start, end, retry)
    else:
        return 'Unsupport packages'


def QA_fetch_get_index_transaction(package, code, start, end, retry=2):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_index_transaction(code, start, end, retry)
    else:
        return 'Unsupport packages'


def QA_fetch_get_stock_transaction_realtime(package, code):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_stock_transaction_realtime(code)
    else:
        return 'Unsupport packages'


def QA_fetch_get_stock_xdxr(package, code):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_stock_xdxr(code)
    else:
        return 'Unsupport packages'


def QA_fetch_get_index_day(package, code, start, end, level='day'):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_index_day(code, start, end, level)
    else:
        return 'Unsupport packages'


def QA_fetch_get_index_min(package, code, start, end, level='1min'):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_index_min(code, start, end, level)
    else:
        return 'Unsupport packages'


def QA_fetch_get_index_realtime(package, code):
    Engine = use(package)
    return Engine.QA_fetch_get_index_realtime(code)


def QA_fetch_get_bond_day(package, code, start, end, level='day'):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_bond_day(code, start, end, level)
    else:
        return 'Unsupport packages'


def QA_fetch_get_bond_min(package, code, start, end, level='1min'):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_bond_min(code, start, end, level)
    else:
        return 'Unsupport packages'


def QA_fetch_get_bond_realtime(package, code):
    Engine = use(package)
    return Engine.QA_fetch_get_bond_realtime(code)


def QA_fetch_get_stock_block(package):
    Engine = use(package)
    if package in ['tdx', 'pytdx', 'ths', 'tushare', 'QA']:
        return Engine.QA_fetch_get_stock_block()
    else:
        return 'Unsupport packages'


def QA_fetch_get_stock_info(package, code):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_stock_info(code)
    else:
        return 'Unsupport packages'

# LIST


def QA_fetch_get_stock_list(package, type_="stock"):
    Engine = use(package)
    if package in ["tdx", "pytdx"]:
        return Engine.QA_fetch_get_stock_list(type_)
    elif package in ["baostock", "bs", "bao"]:
        # baostock 暂不区分 type_，直接返回全部股票列表
        return Engine.QA_fetch_get_stock_list()
    else:
        return "Unsupport packages"


def QA_fetch_get_bond_list(package):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_bond_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_index_list(package):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_index_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_future_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_future_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_option_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_option_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_globalfuture_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_globalfuture_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_hkstock_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_hkstock_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_hkfund_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_hkfund_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_hkindex_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_hkindex_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_usstock_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_usstock_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_macroindex_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_macroindex_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_globalindex_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_globalindex_list()
    else:
        return 'Unsupport packages'


def QA_fetch_get_exchangerate_list(package,):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_exchangerate_list()
    else:
        return 'Unsupport packages'


#######################


def QA_fetch_get_security_bars(code, _type, lens):
    return QATdx.QA_fetch_get_security_bars(code, _type, lens)


def QA_fetch_get_future_transaction(package, code, start, end):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_future_transaction(code, start, end)
    else:
        return 'Unsupport packages'


def QA_fetch_get_future_transaction_realtime(package, code):
    """
    期货实时tick
    """
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_future_transaction_realtime(code)
    else:
        return 'Unsupport packages'


def QA_fetch_get_future_domain():
    return QAKQ.QA_fetch_get_future_domain()


def QA_fetch_get_future_realtime(package, code):
    Engine = use(package)
    return Engine.QA_fetch_get_future_realtime(code)


def QA_fetch_get_future_day(package, code, start, end, frequence='day'):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_future_day(code, start, end, frequence=frequence)
    else:
        return 'Unsupport packages'


def QA_fetch_get_future_min(package, code, start, end, frequence='1min'):
    Engine = use(package)
    if package in ['tdx', 'pytdx']:
        return Engine.QA_fetch_get_future_min(code, start, end, frequence=frequence)
    else:
        return 'Unsupport packages'


def QA_fetch_get_chibor(package, frequence):
    Engine = use(package)
    if package in ['Hexun', 'hexun']:
        return Engine.QA_fetch_get_chibor(frequence)
    else:
        return 'Unsupport packages'


QA_fetch_get_option_day = QA_fetch_get_future_day
QA_fetch_get_option_min = QA_fetch_get_future_min

QA_fetch_get_hkstock_day = QA_fetch_get_future_day
QA_fetch_get_hkstock_min = QA_fetch_get_future_min

QA_fetch_get_hkfund_day = QA_fetch_get_future_day
QA_fetch_get_hkfund_min = QA_fetch_get_future_min

QA_fetch_get_hkindex_day = QA_fetch_get_future_day
QA_fetch_get_hkindex_min = QA_fetch_get_future_min


QA_fetch_get_usstock_day = QA_fetch_get_future_day
QA_fetch_get_usstock_min = QA_fetch_get_future_min

QA_fetch_get_option_day = QA_fetch_get_future_day
QA_fetch_get_option_min = QA_fetch_get_future_min

QA_fetch_get_globalfuture_day = QA_fetch_get_future_day
QA_fetch_get_globalfuture_min = QA_fetch_get_future_min

QA_fetch_get_exchangerate_day = QA_fetch_get_future_day
QA_fetch_get_exchangerate_min = QA_fetch_get_future_min


QA_fetch_get_macroindex_day = QA_fetch_get_future_day
QA_fetch_get_macroindex_min = QA_fetch_get_future_min


QA_fetch_get_globalindex_day = QA_fetch_get_future_day
QA_fetch_get_globalindex_min = QA_fetch_get_future_min
