#coding :utf-8
"""
FOLL-quanda

Quantitative Financial Strategy Framework

by WUJinda

2025
"""

__version__ = '2.1.0.alpha2'
__author__ = 'DAREWIN'

# Rust集成支持检测
try:
    import qars3
    __has_qars__ = True
    __qars_version__ = getattr(qars3, '__version__', 'unknown')
except ImportError:
    __has_qars__ = False
    __qars_version__ = None

try:
    import qadataswap
    __has_dataswap__ = True
    __dataswap_version__ = getattr(qadataswap, '__version__', 'unknown')
except ImportError:
    __has_dataswap__ = False
    __dataswap_version__ = None

import logging
logging.disable(logging.INFO)
import argparse
# check
import sys

# Backtest
# Data
from quanda.QDData import (
    QA_data_calc_marketvalue,
    QA_data_ctptick_resample,
    QA_data_day_resample,
    QA_data_futuremin_resample,
    QA_data_futuremin_resample_series,
    QA_data_futuremin_resample_tb_kq,
    QA_data_futuremin_resample_tb_kq2,
    QA_data_marketvalue,
    QA_data_min_resample,
    QA_data_min_to_day,
    QA_data_stock_to_fq,
    QA_data_tick_resample,
    QA_data_tick_resample_1min,
    QA_data_cryptocurrency_min_resample,
    QA_DataStruct_Day,
    QA_DataStruct_Financial,
    QA_DataStruct_Future_day,
    QA_DataStruct_Future_min,
    QA_DataStruct_Index_day,
    QA_DataStruct_Index_min,
    QA_DataStruct_Indicators,
    QA_DataStruct_Min,
    QA_DataStruct_Series,
    QA_DataStruct_Stock_block,
    QA_DataStruct_Stock_day,
    QA_DataStruct_Stock_min,
    QA_DataStruct_Stock_realtime,
    QA_DataStruct_Stock_transaction,
    QA_DataStruct_CryptoCurrency_day,
    QA_DataStruct_CryptoCurrency_min,
    QDS_IndexDayWarpper,
    QDS_IndexMinWarpper,
    QDS_StockDayWarpper,
    QDS_StockMinWarpper,
    from_tushare
)
from quanda.QDData.dsmethods import *
# ENGINE
from quanda.QDEngine import (
    QA_AsyncQueue,
    QA_AsyncScheduler,
    QA_AsyncTask,
    QA_AsyncThread,
    QA_Engine,
    QA_Event,
    QA_Task,
    QA_Thread,
    QA_Worker
)
from quanda.QDFetch import (
    QA_fetch_get_chibor,
    QA_fetch_get_exchangerate_day,
    QA_fetch_get_exchangerate_list,
    QA_fetch_get_exchangerate_min,
    QA_fetch_get_future_day,
    QA_fetch_get_future_list,
    QA_fetch_get_future_min,
    QA_fetch_get_bond_day,
    QA_fetch_get_bond_min,
    QA_fetch_get_bond_list,
    QA_fetch_get_bond_realtime,
    QA_fetch_get_future_realtime,
    QA_fetch_get_future_domain,
    QA_fetch_get_future_transaction,
    QA_fetch_get_future_transaction_realtime,
    QA_fetch_get_globalfuture_day,
    QA_fetch_get_globalfuture_list,
    QA_fetch_get_globalfuture_min,
    QA_fetch_get_globalindex_day,
    QA_fetch_get_globalindex_list,
    QA_fetch_get_globalindex_min,
    QA_fetch_get_hkfund_day,
    QA_fetch_get_hkfund_list,
    QA_fetch_get_hkfund_min,
    QA_fetch_get_hkindex_day,
    QA_fetch_get_hkindex_list,
    QA_fetch_get_hkindex_min,
    QA_fetch_get_hkstock_day,
    QA_fetch_get_hkstock_list,
    QA_fetch_get_hkstock_min,
    QA_fetch_get_index_day,
    QA_fetch_get_index_list,
    QA_fetch_get_index_min,
    QA_fetch_get_index_realtime,
    QA_fetch_get_macroindex_day,
    QA_fetch_get_macroindex_list,
    QA_fetch_get_macroindex_min,
    QA_fetch_get_option_day,
    QA_fetch_get_option_list,
    QA_fetch_get_option_min,
    QA_fetch_get_security_bars,
    QA_fetch_get_stock_block,
    QA_fetch_get_stock_day,
    QA_fetch_get_stock_info,
    QA_fetch_get_stock_list,
    QA_fetch_get_stock_min,
    QA_fetch_get_stock_realtime,
    QA_fetch_get_stock_transaction,
    QA_fetch_get_stock_transaction_realtime,
    QA_fetch_get_index_transaction,
    QA_fetch_get_stock_xdxr,
    QA_fetch_get_trade_date,
    QA_fetch_get_usstock_day,
    QA_fetch_get_usstock_list,
    QA_fetch_get_usstock_min,
    get_stock_market
)
# fetch methods
from quanda.QDFetch.Fetcher import QA_quotation
from quanda.QDFetch.QDCrawler import (
    QA_fetch_get_sh_margin,
    QA_fetch_get_sz_margin,
    QA_fetch_get_margin_all
)
from quanda.QDFetch.QDQuery import (
    QA_fetch_account,
    QA_fetch_backtest_history,
    QA_fetch_backtest_info,
    QA_fetch_ctp_tick,
    QA_fetch_etf_list,
    QA_fetch_etf_name,
    QA_fetch_financial_report,
    QA_fetch_future_day,
    QA_fetch_future_list,
    QA_fetch_future_min,
    QA_fetch_future_tick,
    QA_fetch_index_day,
    QA_fetch_index_list,
    QA_fetch_index_min,
    QA_fetch_index_name,
    QA_fetch_quotation,
    QA_fetch_quotations,
    QA_fetch_stock_block,
    QA_fetch_stock_day,
    QA_fetch_stock_adj,
    QA_fetch_stock_full,
    QA_fetch_stock_info,
    QA_fetch_stock_list,
    QA_fetch_stock_min,
    QA_fetch_stock_transaction,
    QA_fetch_index_transaction,
    QA_fetch_stock_name,
    QA_fetch_stock_xdxr,
    QA_fetch_trade_date,
    QA_fetch_cryptocurrency_day,
    QA_fetch_cryptocurrency_min,
    QA_fetch_cryptocurrency_list
)
from quanda.QDFetch.QDQuery_Advance import *
from quanda.QDIndicator import *
# market
from quanda.QDFetch.QDClickhouse import QACKClient

from quanda.QDSetting.QDLocalize import (
    cache_path,
    download_path,
    log_path,
    qa_path,
    setting_path
)
# save
from quanda.QDSU.main import (
    QA_SU_save_etf_day,
    QA_SU_save_etf_min,
    QA_SU_save_financialfiles,
    QA_SU_save_future_list,
    QA_SU_save_index_day,
    QA_SU_save_index_list,
    QA_SU_save_index_min,
    QA_SU_save_stock_block,
    QA_SU_save_stock_day,
    QA_SU_save_stock_info,
    QA_SU_save_stock_info_tushare,
    QA_SU_save_stock_list,
    QA_SU_save_stock_min,
    QA_SU_save_stock_min_5,
    QA_SU_save_stock_xdxr
)
from quanda.QDSU.save_strategy import QA_SU_save_strategy
from quanda.QDSU.user import QA_user_sign_in, QA_user_sign_up
from quanda.QDUtil import (  # QAPARAMETER
    AMOUNT_MODEL, BROKER_EVENT, BROKER_TYPE, DATABASE, DATASOURCE,
    ENGINE_EVENT, EXCHANGE_ID, FREQUENCE, MARKET_ERROR, MARKET_EVENT,
    MARKET_TYPE, ORDER_DIRECTION, ORDER_EVENT, ORDER_MODEL, ORDER_STATUS,
    OUTPUT_FORMAT, RUNNING_ENVIRONMENT, RUNNING_STATUS, TRADE_STATUS,
    QA_Setting, QA_util_calc_time, QA_util_cfg_initial, QA_util_code_tolist,
    QA_util_code_tostr, QA_util_date_gap, QA_util_date_int2str,
    QA_util_code_adjust_ctp, QA_util_stamp2datetime,
    QA_util_date_stamp, QA_util_date_str2int, QA_util_date_today,
    QA_util_date_valid, QA_util_dict_remove_key, QA_util_diff_list,
    QA_util_file_md5, QA_util_format_date2str, QA_util_get_cfg,
    QA_util_get_date_index, QA_util_get_index_date, QA_util_get_last_datetime,
    QA_util_get_last_day, QA_util_get_next_datetime, QA_util_get_next_day,
    QA_util_get_next_trade_date, QA_util_get_order_datetime,
    QA_util_get_pre_trade_date, QA_util_get_real_date,
    QA_util_get_real_datelist, QA_util_get_trade_datetime,
    QA_util_get_trade_gap, QA_util_get_trade_range, QA_util_id2date,
    QA_util_if_trade, QA_util_if_tradetime, QA_util_is_trade,
    QA_util_log_debug, QA_util_log_expection, QA_util_log_info,
    QA_util_make_hour_index, QA_util_make_min_index, QA_util_mongo_infos,
    QA_util_mongo_initial, QA_util_mongo_status, QA_util_ms_stamp,
    QA_util_multi_demension_list, QA_util_random_with_topic, QA_util_realtime,
    QA_util_save_csv, QA_util_select_hours, QA_util_select_min,
    QA_util_send_mail, QA_util_sql_async_mongo_setting,
    QA_util_sql_mongo_setting, QA_util_sql_mongo_sort_ASCENDING,
    QA_util_sql_mongo_sort_DESCENDING, QA_util_tdxtimestamp,
    QA_util_time_delay, QA_util_time_gap, QA_util_time_now, QA_util_time_stamp,
    QA_util_to_datetime, QA_util_to_json_from_pandas,
    QA_util_to_list_from_numpy, QA_util_to_list_from_pandas,
    QA_util_to_pandas_from_json, QA_util_to_pandas_from_list, QA_util_web_ping,
    QATZInfo_CN, future_ip_list, info_ip_list, stock_ip_list, trade_date_sse,
    QA_util_get_next_period, QA_util_get_real_tradeday)

# QAResourceManager - 统一资源管理器 (MongoDB/RabbitMQ/ClickHouse/Redis)
try:
    from quanda.QDUtil.QDResourceManager import (
        QAMongoResourceManager,
        QARabbitMQResourceManager,
        QAClickHouseResourceManager,
        QARedisResourceManager,
        QAResourcePool,
        get_mongo_resource,
        get_rabbitmq_resource,
        get_clickhouse_resource,
        get_redis_resource,
    )
except ImportError:
    # 资源管理器依赖可选,不阻塞主模块加载
    pass

from quanda.QDPubSub.consumer import subscriber, subscriber_topic, subscriber_routing
from quanda.QDPubSub.producer import publisher, publisher_topic, publisher_routing
from quanda.QDPubSub.base import base_ps
from quanda.QDPubSub.debugtoool import debug_sub, debug_pub


from quanda.QDWebServer.basehandles import QDBaseHandler, QDWebSocketHandler
from quanda.QDWebServer.server import start_server

from quanda.QIFI.QifiAccount import QIFI_Account
from quanda.QIFI.QifiManager import QA_QIFIMANAGER, QA_QIFISMANAGER

# QAMarket - 市场预设和订单/持仓管理
from quanda.QDMarket import (
    MARKET_PRESET,
    QA_Order,
    QA_OrderQueue,
    QA_Position,
    QA_PMS,
)

# QARSBridge - Rust高性能账户和回测 (已移除)
# QADataBridge - 跨语言零拷贝数据交换 (已移除)

from quanda.QDStrategy.qactabase import QAStrategyCtaBase

# Python 3.9-3.12 (与 setup.py 及 QARS2 对齐)
if sys.version_info < (3, 9) or sys.version_info >= (4, 0):
    print('quanda 2.1+ 需要 Python 3.9-3.12，当前: {}.{}.{}'.format(
        sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    sys.exit(1)

#QA_util_log_info('Welcome to quanda, the Version is {}'.format(__version__))


def __repr__():
    return ' \n \
            ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````````` \n \
            ``########`````##````````##``````````##`````````####````````##```##########````````#``````##``````###```##`````######`` \n \
            `##``````## ```##````````##`````````####````````##`##```````##```````##```````````###``````##````##`````##```##`````##` \n \
            ##````````##```##````````##````````##`##````````##``##``````##```````##``````````####```````#```##``````##```##``````## \n \
            ##````````##```##````````##```````##```##```````##```##`````##```````##`````````##`##```````##`##```````##````##``````` \n \
            ##````````##```##````````##``````##`````##``````##````##````##```````##````````##``###```````###````````##`````##`````` \n \
            ##````````##```##````````##``````##``````##`````##`````##```##```````##```````##````##```````###````````##``````###```` \n \
            ##````````##```##````````##`````##````````##````##``````##``##```````##``````##``````##`````##`##```````##````````##``` \n \
            ##````````##```##````````##````#############````##```````##`##```````##`````###########`````##``##``````##`````````##`` \n \
            ###```````##```##````````##```##```````````##```##```````##`##```````##````##`````````##```##```##``````##```##`````##` \n \
            `##``````###````##``````###``##`````````````##``##````````####```````##```##``````````##``###````##`````##````##`````## \n \
            ``#########``````########```##``````````````###`##``````````##```````##``##````````````##`##``````##````##`````###``### \n \
            ````````#####`````````````````````````````````````````````````````````````````````````````````````````````````````##``  \n \
            ``````````````````````````````````````````````````````````````````````````````````````````````````````````````````````` \n \
            ``````````````````````````Copyright``QuanDA``2025``````QUANTITATIVE FINANCIAL FRAMEWORK````````````````````````````` \n \
            ``````````````````````````````````````````````````````````````````````````````````````````````````````````````````````` \n \
            ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````````` \n \
            ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````````` \n '


__str__ = __repr__
