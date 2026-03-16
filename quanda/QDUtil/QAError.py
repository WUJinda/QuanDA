# coding:utf-8
#
# The MIT License (MIT)
#
"""quanda 的error类

"""


class QAError_fetch_data(RuntimeError):
    def __init__(self, res):
        RuntimeError.__init__(self, 'QA FETCH DATA ERROR', res)


class QAError_no_data_in_database(RuntimeError):
    def __init__(self, res):
        RuntimeError.__init__(self, 'QA FETCH NO DATA ERROR', res)


class QAError_crawl_data_web(RuntimeError):
    def __init__(self, res):
        RuntimeError.__init__(self, 'QA CRAWLER ERROR', res)


class QAError_database_connection(RuntimeError):
    def __init__(self, res):
        RuntimeError.__init__(self, 'QA DATABASE CONNECTION ERROR', res)


class QAError_web_connection(RuntimeError):
    def __init__(self, res):
        RuntimeError.__init__(self, 'QA WEB CONNECTION ERROR', res)


class QAError_market_enging_down(RuntimeError):
    def __init__(self, res):
        RuntimeError.__init__(self, 'QA MARKET ENGING DOWN ERROR', res)
