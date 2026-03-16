# coding=utf-8
#
# The MIT License (MIT)
#
import subprocess

import pandas as pd

from quanda.QDUtil.QASetting import DATABASE
from quanda.QDUtil.QALogs import QA_util_log_info


def QA_util_mongo_initial(db=DATABASE):

    db.drop_collection('stock_day')
    db.drop_collection('stock_list')
    db.drop_collection('stock_info')
    db.drop_collection('trade_date')
    db.drop_collection('stock_min')
    db.drop_collection('stock_transaction')
    db.drop_collection('stock_xdxr')





def QA_util_mongo_status(db=DATABASE):
    QA_util_log_info(list(db.list_collection_names()))
    try:
        QA_util_log_info(db.client.admin.command('serverStatus'))
    except Exception:
        pass
    QA_util_log_info(subprocess.call('mongostat', shell=True))


def QA_util_mongo_infos(db=DATABASE):

    data_struct = []

    for item in db.list_collection_names():
        coll = db[item]
        value = []
        value.append(item)
        value.append(coll.count_documents({}))
        doc = coll.find_one()
        value.append(list(doc.keys()) if doc else [])
        data_struct.append(value)
    return pd.DataFrame(data_struct, columns=['collection_name', 'counts', 'columns']).set_index('collection_name')


if __name__ == '__main__':
    print(QA_util_mongo_infos())
    QA_util_mongo_status()
