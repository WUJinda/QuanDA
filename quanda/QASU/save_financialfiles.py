# coding:utf-8
#
# The MIT License (MIT)
#
import os
import sys

import pymongo

from quanda.QAFetch.QAfinancial import (download_financialzip, parse_all,
                                           parse_filelist,download_financialzip_fromtdx)
from quanda.QASetting.QALocalize import (cache_path, download_path, qa_path,
                                            setting_path)
from quanda.QAUtil import DATABASE, QA_util_date_int2str
from quanda.QAUtil.QASql import ASCENDING, DESCENDING
from quanda.QAUtil.QATransform import QA_util_to_json_from_pandas
import datetime


def QA_SU_save_financial_files(fromtdx=False):
    """本地存储financialdata
    """
    if (fromtdx):
        download_financialzip_fromtdx()
    else:
        download_financialzip()
        
    coll = DATABASE.financial
    coll.create_index(
        [("code", ASCENDING), ("report_date", ASCENDING)], unique=True)
    for item in os.listdir(download_path):
        if item[0:4] != 'gpcw':
            print(
                "file ", item, " is not start with gpcw , seems not a financial file , ignore!")
            continue

        date = int(item.split('.')[0][-8:])
        print('quanda NOW SAVING {}'.format(date))
        print('在数据库中的条数 {}'.format(coll.count_documents({'report_date': date})))
        try:
            data = QA_util_to_json_from_pandas(parse_filelist([item]).reset_index(
            ).drop_duplicates(subset=['code', 'report_date']).sort_index())
            print('即将更新的条数 {}'.format(len(data)))
            # data["crawl_date"] = str(datetime.date.today())
            try:
                for d in data:
                    coll.update_one({'code': d['code'], 'report_date': d['report_date']}, {'$set': d}, upsert=True)

            except Exception as e:
                if isinstance(e, MemoryError):
                    coll.insert_many(data, ordered=True)
                elif isinstance(e, pymongo.bulk.BulkWriteError):
                    pass
        except Exception as e:
            print('似乎没有数据')



    print('SUCCESSFULLY SAVE/UPDATE FINANCIAL DATA')

