# coding:utf-8
"""
策略参考库 Handler
提供策略参考的增删改查、图片上传、K线区间分析等功能
"""

import json
import os
import uuid
import datetime
import base64
from typing import Dict, List
import pandas as pd
import numpy as np
from quanda.QAWebServer.basehandles import QABaseHandler
from quanda.QAUtil import QA_util_to_json_from_pandas
from qaenv import mongo_ip
from pymongo import MongoClient


class StrategyReferenceListHandler(QABaseHandler):
    """获取策略参考列表"""
    
    def get(self):
        try:
            client = MongoClient(mongo_ip)
            db = client.quanda
            collection = db.strategy_reference
            
            # 获取过滤参数
            pattern = self.get_argument('pattern', None)
            trend = self.get_argument('trend', None)
            frequence = self.get_argument('frequence', None)
            
            query = {}
            if pattern:
                query['pattern.type'] = pattern
            if trend:
                query['pattern.trend'] = trend
            if frequence:
                query['frequence'] = frequence
            
            # 查询数据
            data = list(collection.find(query, {'_id': 0}).sort('createTime', -1))
            
            self.write({
                'status': 200,
                'res': data
            })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取策略参考列表失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': []
            })


class StrategyReferenceDetailHandler(QABaseHandler):
    """获取策略参考详情"""
    
    def get(self, ref_id):
        try:
            client = MongoClient(mongo_ip)
            db = client.quanda
            collection = db.strategy_reference
            
            data = collection.find_one({'id': ref_id}, {'_id': 0})
            
            if data:
                self.write({
                    'status': 200,
                    'res': data
                })
            else:
                self.write({
                    'status': 404,
                    'message': '策略参考不存在',
                    'res': None
                })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取策略参考详情失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': None
            })


class StrategyReferenceCreateHandler(QABaseHandler):
    """创建策略参考"""
    
    def post(self):
        try:
            data = json.loads(self.request.body)
            
            # 生成ID和时间戳
            ref_id = str(uuid.uuid4())
            now = datetime.datetime.now().isoformat()
            
            reference = {
                'id': ref_id,
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'image': data.get('image', ''),
                'code': data.get('code', ''),
                'frequence': data.get('frequence', 'day'),
                'startTime': data.get('startTime', ''),
                'endTime': data.get('endTime', ''),
                'pattern': data.get('pattern', {}),
                'indicators': data.get('indicators', {}),
                'klineData': data.get('klineData', []),
                'tags': data.get('tags', []),
                'createTime': now,
                'updateTime': now
            }
            
            client = MongoClient(mongo_ip)
            db = client.quanda
            collection = db.strategy_reference
            
            collection.insert_one(reference)
            
            self.write({
                'status': 200,
                'message': '创建成功',
                'res': reference
            })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'创建策略参考失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': None
            })


class StrategyReferenceUpdateHandler(QABaseHandler):
    """更新策略参考"""
    
    def put(self, ref_id):
        try:
            data = json.loads(self.request.body)
            data['updateTime'] = datetime.datetime.now().isoformat()
            
            client = MongoClient(mongo_ip)
            db = client.quanda
            collection = db.strategy_reference
            
            result = collection.update_one(
                {'id': ref_id},
                {'$set': data}
            )
            
            if result.modified_count > 0:
                self.write({
                    'status': 200,
                    'message': '更新成功',
                    'res': data
                })
            else:
                self.write({
                    'status': 404,
                    'message': '策略参考不存在',
                    'res': None
                })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'更新策略参考失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': None
            })


class StrategyReferenceDeleteHandler(QABaseHandler):
    """删除策略参考"""
    
    def delete(self, ref_id):
        try:
            client = MongoClient(mongo_ip)
            db = client.quanda
            collection = db.strategy_reference
            
            result = collection.delete_one({'id': ref_id})
            
            if result.deleted_count > 0:
                self.write({
                    'status': 200,
                    'message': '删除成功',
                    'res': True
                })
            else:
                self.write({
                    'status': 404,
                    'message': '策略参考不存在',
                    'res': False
                })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'删除策略参考失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': False
            })


class StrategyReferenceUploadHandler(QABaseHandler):
    """上传截图"""
    
    def post(self):
        try:
            # 获取上传的文件
            file_data = self.request.files.get('file', [])
            if not file_data:
                self.write({
                    'status': 400,
                    'message': '未找到上传文件',
                    'res': None
                })
                return
            
            file_info = file_data[0]
            filename = file_info['filename']
            body = file_info['body']
            
            # 生成唯一文件名
            ext = os.path.splitext(filename)[1]
            new_filename = f"{uuid.uuid4()}{ext}"
            
            # 保存文件到 uploads 目录
            upload_dir = 'uploads/strategy-reference'
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, new_filename)
            with open(file_path, 'wb') as f:
                f.write(body)
            
            # 返回文件URL
            file_url = f'/uploads/strategy-reference/{new_filename}'
            
            self.write({
                'status': 200,
                'message': '上传成功',
                'res': {'url': file_url}
            })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'上传失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': None
            })


class StrategyReferenceAnalyzeHandler(QABaseHandler):
    """分析K线区间"""
    
    def post(self):
        try:
            data = json.loads(self.request.body)
            code = data.get('code')
            start = data.get('start')
            end = data.get('end')
            frequence = data.get('frequence', 'day')
            
            # 获取K线数据
            from quanda.QAWebServer.handlers.datahandler import get_future_data_safe
            df = get_future_data_safe(code, start, end, frequence)
            
            if df is None or df.empty:
                self.write({
                    'status': 404,
                    'message': '未找到数据',
                    'res': None
                })
                return
            
            # 计算BOLL指标
            close_prices = df['close'].values
            period = 20
            multiplier = 2
            
            boll_upper = []
            boll_middle = []
            boll_lower = []
            
            for i in range(len(close_prices)):
                if i < period - 1:
                    boll_upper.append(None)
                    boll_middle.append(None)
                    boll_lower.append(None)
                else:
                    slice_data = close_prices[i - period + 1:i + 1]
                    mean = np.mean(slice_data)
                    std = np.std(slice_data)
                    
                    boll_middle.append(float(mean))
                    boll_upper.append(float(mean + multiplier * std))
                    boll_lower.append(float(mean - multiplier * std))
            
            # 计算MA
            ma5 = df['close'].rolling(window=5).mean().tolist()
            ma10 = df['close'].rolling(window=10).mean().tolist()
            ma20 = df['close'].rolling(window=20).mean().tolist()
            
            # 判断趋势
            first_close = close_prices[0]
            last_close = close_prices[-1]
            price_change = ((last_close - first_close) / first_close) * 100
            
            if price_change > 2:
                trend = 'up'
            elif price_change < -2:
                trend = 'down'
            else:
                trend = 'sideways'
            
            # 判断BOLL位置
            last_price = close_prices[-1]
            last_upper = boll_upper[-1] if boll_upper[-1] else last_price
            last_middle = boll_middle[-1] if boll_middle[-1] else last_price
            last_lower = boll_lower[-1] if boll_lower[-1] else last_price
            
            if last_price > last_upper:
                boll_position = 'upper'
            elif last_price < last_lower:
                boll_position = 'lower'
            elif abs(last_price - last_middle) < (last_upper - last_middle) * 0.2:
                boll_position = 'middle'
            else:
                boll_position = 'between'
            
            # 计算波动率
            volatility = float(np.std(close_prices) / np.mean(close_prices) * 100)
            
            # 构建返回数据
            result = {
                'pattern': {
                    'type': 'custom',
                    'bollPosition': boll_position,
                    'trend': trend,
                    'description': f'区间涨跌幅: {price_change:.2f}%, 波动率: {volatility:.2f}%'
                },
                'indicators': {
                    'boll': {
                        'upper': [x for x in boll_upper if x is not None],
                        'middle': [x for x in boll_middle if x is not None],
                        'lower': [x for x in boll_lower if x is not None]
                    },
                    'ma': {
                        'ma5': [x for x in ma5 if not pd.isna(x)],
                        'ma10': [x for x in ma10 if not pd.isna(x)],
                        'ma20': [x for x in ma20 if not pd.isna(x)]
                    },
                    'volume': df['volume'].tolist(),
                    'priceChange': float(price_change),
                    'volatility': volatility
                },
                'klineData': QA_util_to_json_from_pandas(df)
            }
            
            self.write({
                'status': 200,
                'res': result
            })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'分析失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': None
            })
