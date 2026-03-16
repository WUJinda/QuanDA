# coding:utf-8
"""
QuanDA 配置环境变量兼容模块

该模块提供向后兼容的配置接口，将 qaenv 风格的配置映射到新的 QASETTING 系统。

@version: 2.0.0
@author: DAREWIN
"""

import os

# MongoDB 配置
# 优先从环境变量读取，否则使用默认值
mongo_ip = os.getenv('MONGODB', 'localhost')
mongo_port = int(os.getenv('MONGODB_PORT', '27017'))
mongo_uri = f'mongodb://{mongo_ip}:{mongo_port}'

# 数据库配置
database = os.getenv('MONGODB_DATABASE', 'quanda')

# ClickHouse 配置
clickhouse_ip = os.getenv('CLICKHOUSE_HOST', 'localhost')
clickhouse_port = int(os.getenv('CLICKHOUSE_PORT', '9000'))
clickhouse_user = os.getenv('CLICKHOUSE_USER', 'default')
clickhouse_password = os.getenv('CLICKHOUSE_PASSWORD', '')
clickhouse_database = os.getenv('CLICKHOUSE_DATABASE', 'default')

# RabbitMQ/EventMQ 配置
eventmq_ip = os.getenv('EVENTMQ_HOST', 'localhost')
eventmq_port = int(os.getenv('EVENTMQ_PORT', '5672'))
eventmq_username = os.getenv('EVENTMQ_USER', 'guest')
eventmq_password = os.getenv('EVENTMQ_PASSWORD', 'guest')
eventmq_amqp = os.getenv('EVENTMQ_AMQP', 'amqp://guest:guest@localhost:5672/')

# 其他配置（如果需要）
# 可以根据实际需求添加更多配置项
