#
# The MIT License (MIT)
#
from quanda.QAIndicator.indicators import *
from quanda.QAIndicator.base import *
try:
    from quanda.QAIndicator.talib_series import *
    from quanda.QAIndicator.talib_numpy import *
    from quanda.QAIndicator import talib_indicators as talib_qa
except:
    print('PLEASE install TALIB to call these methods')
"""
这个模块是对了对应QA_DataStruct

可以被add_func来添加,所以 这个模块的函数必须有一个DataFrame的输入


例如

import quanda as QA
data=QA.QA_fetch_stock_day_adv('000001','2017-01-01','2017-01-31')
data.add_func(QA.)
"""
