# coding:utf-8
#
# The MIT License (MIT)
#
"""quanda访问获取QAWEB的行情

233333 结果变成自己访问自己了
"""
import  pandas as pd
from quanda.QDUtil.QACode import QA_util_code_tostr


def QA_fetch_get_stock_day(code, start, end, ip='192.168.0.1', port='8010'):
    pass
    # requests.get(


def QA_fetch_get_stock_block():
    """ths的版块数据

    Returns:
        [type] -- [description]
    """

    url = 'http://data.yutiansut.com/self_block.csv'
    try:
        bl = pd.read_csv(url)
        return bl.assign(code=bl['证券代码'].apply(QA_util_code_tostr), blockname=bl['行业'], name=bl['证券名称'], source='outside', type='outside').set_index('code', drop=False)
    except Exception as e:
        print(e)
        return None


if __name__ == "__main__":
    print(QA_fetch_get_stock_block())