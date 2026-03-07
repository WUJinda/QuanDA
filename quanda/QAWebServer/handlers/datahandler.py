# coding:utf-8
"""
数据接口 Handler
提供期货、股票等市场数据的 RESTful API
"""

import json
import pandas as pd
from quanda.QAWebServer.basehandles import QABaseHandler
from quanda.QAUtil import QA_util_to_json_from_pandas
import quanda as QA

# 尝试从不同数据源获取数据
def get_future_list_safe():
    """安全获取期货列表，优先使用MongoDB，失败则返回常用期货代码"""
    try:
        # 尝试从MongoDB获取
        from qaenv import mongo_ip
        from pymongo import MongoClient
        client = MongoClient(mongo_ip)
        db = client.quantaxis
        data = list(db.future_list.find({}, {'code': 1, '_id': 0}))
        if data:
            return [item['code'] for item in data]
    except:
        pass
    
    try:
        # 尝试从TDX获取
        from quanda.QAFetch.QATdx import QA_fetch_get_future_list
        data = QA_fetch_get_future_list()
        if data is not None and not data.empty:
            return data['code'].tolist()
    except:
        pass
    
    # 返回常用期货代码作为fallback
    return [
        'IF2403', 'IF2404', 'IF2406', 'IF2409',  # 沪深300股指期货
        'IC2403', 'IC2404', 'IC2406', 'IC2409',  # 中证500股指期货
        'IH2403', 'IH2404', 'IH2406', 'IH2409',  # 上证50股指期货
        'IM2403', 'IM2404', 'IM2406', 'IM2409',  # 中证1000股指期货
        'T2403', 'T2406', 'T2409', 'T2412',      # 10年期国债期货
        'TF2403', 'TF2406', 'TF2409', 'TF2412',  # 5年期国债期货
        'TS2403', 'TS2406', 'TS2409', 'TS2412',  # 2年期国债期货
    ]


def get_future_data_safe(code, start, end, frequence='day'):
    """安全获取期货数据"""
    try:
        # 优先从MongoDB获取
        from qaenv import mongo_ip
        from pymongo import MongoClient
        client = MongoClient(mongo_ip)
        db = client.quantaxis
        
        query = {
            'code': code,
            'date': {'$gte': start, '$lte': end}
        }
        
        data = list(db.future_day.find(query, {'_id': 0}).sort('date', 1))
        
        if data:
            return pd.DataFrame(data)
    except Exception as e:
        print(f"MongoDB查询失败: {e}")
        pass
    
    try:
        # 尝试从TDX获取
        from quanda.QAFetch.QATdx import QA_fetch_get_future_day, QA_fetch_get_future_min
        if frequence in ['day', 'week', 'month']:
            data = QA_fetch_get_future_day(code, start, end, frequence)
        else:
            data = QA_fetch_get_future_min(code, start, end, frequence)
        
        if data is not None and not data.empty:
            return data
    except:
        pass
    
    return None


class QAFutureListHandler(QABaseHandler):
    """获取期货列表"""
    
    def get(self):
        try:
            result = get_future_list_safe()
            self.write({
                'status': 200,
                'res': result
            })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取期货列表失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': []
            })


class QAFutureDayHandler(QABaseHandler):
    """获取期货日线数据"""
    
    def get(self):
        try:
            code = self.get_argument('code')
            start = self.get_argument('start')
            end = self.get_argument('end')
            frequence = self.get_argument('frequence', 'day')
            
            # 获取期货数据
            data = get_future_data_safe(code, start, end, frequence)
            
            if data is not None and not data.empty:
                # 转换为 JSON 格式
                result = QA_util_to_json_from_pandas(data)
                self.write({
                    'status': 200,
                    'res': result
                })
            else:
                self.write({
                    'status': 200,
                    'message': '暂无数据，请先初始化数据到MongoDB',
                    'res': []
                })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取期货日线数据失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': []
            })


class QAFutureMinHandler(QABaseHandler):
    """获取期货分钟数据"""
    
    def get(self):
        try:
            code = self.get_argument('code')
            start = self.get_argument('start')
            end = self.get_argument('end')
            frequence = self.get_argument('frequence', '1min')
            
            # 获取期货分钟数据
            data = get_future_data_safe(code, start, end, frequence)
            
            if data is not None and not data.empty:
                # 转换为 JSON 格式
                result = QA_util_to_json_from_pandas(data)
                self.write({
                    'status': 200,
                    'res': result
                })
            else:
                self.write({
                    'status': 200,
                    'message': '暂无数据，请先初始化数据到MongoDB',
                    'res': []
                })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取期货分钟数据失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': []
            })


class QAFutureRealtimeHandler(QABaseHandler):
    """获取期货实时数据"""
    
    def get(self):
        try:
            code = self.get_argument('code')
            
            # 尝试获取实时数据
            try:
                from quanda.QAFetch.QATdx import QA_fetch_get_future_realtime
                data = QA_fetch_get_future_realtime(code)
                if data is not None and not data.empty:
                    result = data.reset_index().to_dict('records')[0]
                    self.write({
                        'status': 200,
                        'res': result
                    })
                    return
            except:
                pass
            
            # 如果实时数据获取失败，返回空数据
            self.write({
                'status': 200,
                'message': '实时数据暂不可用',
                'res': {
                    'code': code,
                    'price': 0,
                    'open': 0,
                    'high': 0,
                    'low': 0,
                    'volume': 0,
                    'change': 0,
                    'changePercent': 0
                }
            })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取期货实时数据失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': {}
            })
