# coding:utf-8
"""
数据库索引初始化脚本
为策略管理和回测系统创建必要的索引
"""
import pymongo
from qaenv import mongo_ip


def init_database_indexes():
    """初始化数据库索引"""
    client = pymongo.MongoClient(mongo_ip)
    db = client.quanda

    # 策略集合索引
    db.strategies.create_index([('id', 1)], unique=True)
    db.strategies.create_index([('status', 1)])
    db.strategies.create_index([('type', 1)])
    db.strategies.create_index([('create_time', -1)])

    # 回测任务集合索引
    db.backtest_tasks.create_index([('backtest_id', 1)], unique=True)
    db.backtest_tasks.create_index([('status', 1)])
    db.backtest_tasks.create_index([('create_time', -1)])

    # 回测结果集合索引
    db.backtest_results.create_index([('backtest_id', 1)], unique=True)

    print("数据库索引创建完成")


if __name__ == '__main__':
    init_database_indexes()
