# coding:utf-8
#
# The MIT License (MIT)
#
""""
QuanDA
util tool
"""
# path

# bar
from quanda.QDUtil.QDBar import (QA_util_make_hour_index,
                                    QA_util_make_min_index, QA_util_time_gap)
from quanda.QDUtil.QDCache import QA_util_cache
# config
from quanda.QDUtil.QDCfg import QA_util_cfg_initial, QA_util_get_cfg
# code function
from quanda.QDUtil.QDCode import QA_util_code_tolist, QA_util_code_tostr, QA_util_code_adjust_ctp, QA_util_code_change_format
# csv
from quanda.QDUtil.QDCsv import QA_util_save_csv
# date
from quanda.QDUtil.QDDate import (QA_util_calc_time, QA_util_date_int2str,
                                     QA_util_date_stamp, QA_util_date_str2int,
                                     QA_util_date_today, QA_util_date_valid,
                                     QA_util_datetime_to_strdate,
                                     QA_util_stamp2datetime,
                                     QA_util_get_date_index,
                                     QA_util_tdxtimestamp,
                                     QA_util_get_index_date, QA_util_id2date,
                                     QA_util_is_trade, QA_util_ms_stamp,
                                     QA_util_realtime, QA_util_select_hours,
                                     QA_util_select_min, QA_util_time_delay,
                                     QA_util_time_now, QA_util_time_stamp,
                                     QA_util_to_datetime, QA_util_today_str,
                                     QATZInfo_CN)
# trade date
from quanda.QDUtil.QDDate_trade import (QA_util_date_gap,
                                           QA_util_format_date2str,
                                           QA_util_future_to_realdatetime,
                                           QA_util_future_to_tradedatetime,
                                           QA_util_get_last_datetime,
                                           QA_util_get_last_day,
                                           QA_util_get_next_datetime,
                                           QA_util_get_next_day,
                                           QA_util_get_next_trade_date,
                                           QA_util_get_order_datetime,
                                           QA_util_get_pre_trade_date,
                                           QA_util_get_real_date,
                                           QA_util_get_real_tradeday,
                                           QA_util_get_real_datelist,
                                           QA_util_get_trade_datetime,
                                           QA_util_get_trade_gap,
                                           QA_util_get_trade_range,
                                           QA_util_if_trade,
                                           QA_util_if_tradetime,
                                           QA_util_get_next_day,
                                           QA_util_get_last_day,
                                           QA_util_get_last_datetime,
                                           QA_util_get_next_datetime,
                                           QA_util_get_order_datetime,
                                           QA_util_get_trade_datetime,
                                           QA_util_future_to_realdatetime,
                                           QA_util_future_to_tradedatetime,
                                           trade_date_sse,
                                           QA_util_get_next_period)
# datetolls
from quanda.QDUtil.QDDateTools import (QA_util_add_months,
                                          QA_util_get_1st_of_next_month,
                                          QA_util_getBetweenMonth,
                                          QA_util_getBetweenQuarter)
# dict function
from quanda.QDUtil.QDDict import QA_util_dict_remove_key
from quanda.QDUtil.QDFile import QA_util_file_md5
# list function
from quanda.QDUtil.QDList import (QA_util_diff_list,
                                     QA_util_multi_demension_list)

# code function
from quanda.QDUtil.QDCode import QA_util_code_tostr, QA_util_code_tolist
# dict function
from quanda.QDUtil.QDDict import QA_util_dict_remove_key
# log
from quanda.QDUtil.QDLogs import (QA_util_log_debug, QA_util_log_expection,
                                     QA_util_log_info)
# MongoDB
from quanda.QDUtil.QDMongo import (QA_util_mongo_infos,
                                      QA_util_mongo_initial,
                                      QA_util_mongo_status)
# Parameter
from quanda.QDUtil.QDParameter import (
    ACCOUNT_EVENT, AMOUNT_MODEL, BROKER_EVENT, BROKER_TYPE, DATASOURCE,
    ENGINE_EVENT, EVENT_TYPE, EXCHANGE_ID, FREQUENCE, MARKET_ERROR,
    MARKET_EVENT, MARKET_TYPE, ORDER_DIRECTION, ORDER_EVENT, ORDER_MODEL,
    TIME_CONDITION, VOLUME_CONDITION,
    ORDER_STATUS, OUTPUT_FORMAT, RUNNING_ENVIRONMENT, TRADE_STATUS, RUNNING_STATUS)
# RANDOM class
from quanda.QDUtil.QDRandom import QA_util_random_with_topic
from quanda.QDUtil.QDSetting import (DATABASE, QASETTING, QA_Setting,
                                        exclude_from_stock_ip_list,
                                        future_ip_list, info_ip_list,
                                        stock_ip_list)
from quanda.QDUtil.QDSingleton import singleton
# sql
from quanda.QDUtil.QDSql import (QA_util_sql_async_mongo_setting,
                                    QA_util_sql_mongo_setting,
                                    QA_util_sql_mongo_sort_ASCENDING,
                                    QA_util_sql_mongo_sort_DESCENDING)
# format
from quanda.QDUtil.QDTransform import (QA_util_to_json_from_pandas,
                                          QA_util_to_list_from_numpy,
                                          QA_util_to_list_from_pandas,
                                          QA_util_to_pandas_from_json,
                                          QA_util_to_pandas_from_list)

# 网络相关
from quanda.QDUtil.QDWebutil import QA_util_web_ping
from quanda.QDUtil.QDMail import QA_util_send_mail

# 文件相关

from quanda.QDUtil.QDFile import QA_util_file_md5

# datetolls
from quanda.QDUtil.QDDateTools import (
    QA_util_getBetweenQuarter, QA_util_get_1st_of_next_month,
    QA_util_add_months, QA_util_getBetweenMonth
)

from quanda.QDUtil.Parallelism import Parallelism, Parallelism_Thread
from quanda.QDUtil.QDCache import QA_util_cache
from quanda.QDUtil.QDSingleton import singleton

import platform
from functools import wraps
platform_flag = platform.system() == 'Windows'

if not platform_flag:
    from resource import getrusage as resource_usage, RUSAGE_SELF
    from time import time as timestamp

    def print_used_time(func):
        ''' 打印运行时间

        :param func: 运行的函数名称
        :return:
        '''

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time, start_resources = timestamp(), resource_usage(RUSAGE_SELF)
            func(*args, **kwargs)
            end_resources, end_time = resource_usage(RUSAGE_SELF), timestamp()
            print({'消耗时间': {'real': end_time - start_time,
                            'sys': end_resources.ru_stime - start_resources.ru_stime,
                            'user': end_resources.ru_utime - start_resources.ru_utime}})
            return True
        return wrapper
else:
    def print_used_time(func):
        ''' 打印运行时间

        :param func: 运行的函数名称
        :return:
        '''

        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            return True

        return wrapper
