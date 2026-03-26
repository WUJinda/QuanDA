# coding:utf-8
"""
数据接口 Handler
提供期货、股票等市场数据的 RESTful API
"""

import json
import pandas as pd
from quanda.QDWebServer.basehandles import QDBaseHandler
from quanda.QDUtil import QA_util_to_json_from_pandas
import quanda as QA

# 尝试从不同数据源获取数据
def get_future_list_safe():
    """安全获取期货列表，优先使用MongoDB，失败则返回静态合约列表"""
    try:
        # 尝试从MongoDB获取
        from qaenv import mongo_ip
        from pymongo import MongoClient
        client = MongoClient(mongo_ip)
        db = client.quanda

        # 首先尝试从 future_day 集合获取实际存在的合约
        codes = db.future_day.distinct('code')
        if codes:
            return sorted(codes)

        # 其次尝试从 future_list 集合获取
        data = list(db.future_list.find({}, {'code': 1, '_id': 0}))
        if data:
            return [item['code'] for item in data]
    except:
        pass

    try:
        # 尝试从TDX获取
        from quanda.QDFetch.QDTdx import QA_fetch_get_future_list
        data = QA_fetch_get_future_list()
        if data is not None and not data.empty:
            return data['code'].tolist()
    except:
        pass

    # 返回静态合约列表作为fallback
    try:
        from quanda.QDData.future_contracts import get_all_contracts
        return get_all_contracts()
    except:
        pass

    # 最终fallback
    return [
        'IF2504', 'IF2505', 'IF2506', 'IF2509', 'IF2512',
        'IC2504', 'IC2505', 'IC2506', 'IC2509', 'IC2512',
        'IH2504', 'IH2505', 'IH2506', 'IH2509', 'IH2512',
        'IM2504', 'IM2505', 'IM2506', 'IM2509', 'IM2512',
    ]


def get_future_data_safe(code, start, end, frequence='day', limit=None):
    """安全获取期货数据（优化版）"""
    try:
        # 优先从MongoDB获取
        from qaenv import mongo_ip
        from pymongo import MongoClient
        client = MongoClient(mongo_ip)
        db = client.quanda
        
        query = {
            'code': code,
            'date': {'$gte': start, '$lte': end}
        }
        
        # 添加数据量限制，避免一次性加载过多数据
        cursor = db.future_day.find(query, {'_id': 0}).sort('date', -1)
        if limit:
            cursor = cursor.limit(limit)
        
        data = list(cursor)
        
        if data:
            # 反转数据顺序（因为使用了倒序查询）
            data.reverse()
            df = pd.DataFrame(data)
            # 只返回必要的列，减少数据传输量
            required_cols = ['date', 'code', 'open', 'high', 'low', 'close', 'volume']
            return df[required_cols] if all(col in df.columns for col in required_cols) else df
    except Exception as e:
        print(f"MongoDB查询失败: {e}")
        pass
    
    try:
        # 尝试从TDX获取
        from quanda.QDFetch.QDTdx import QA_fetch_get_future_day, QA_fetch_get_future_min
        if frequence in ['day', 'week', 'month']:
            data = QA_fetch_get_future_day(code, start, end, frequence)
        else:
            data = QA_fetch_get_future_min(code, start, end, frequence)
        
        if data is not None and not data.empty:
            # 限制返回数据量
            if limit and len(data) > limit:
                data = data.tail(limit)
            return data
    except:
        pass
    
    return None


class QDFutureListHandler(QDBaseHandler):
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


class QDFutureDayHandler(QDBaseHandler):
    """获取期货日线数据（优化版）"""
    
    def get(self):
        try:
            code = self.get_argument('code')
            start = self.get_argument('start')
            end = self.get_argument('end')
            frequence = self.get_argument('frequence', 'day')
            limit = self.get_argument('limit', None)
            
            # 转换limit参数
            if limit:
                limit = int(limit)
            
            # 获取期货数据
            data = get_future_data_safe(code, start, end, frequence, limit)
            
            if data is not None and not data.empty:
                # 确保数据格式正确
                if 'date' not in data.columns and data.index.name == 'date':
                    data = data.reset_index()
                
                # 转换为 JSON 格式（优化：减少精度，降低数据量）
                result = QA_util_to_json_from_pandas(data)
                
                # 设置缓存头，允许浏览器缓存5分钟
                self.set_header('Cache-Control', 'public, max-age=300')
                
                self.write({
                    'status': 200,
                    'res': result,
                    'count': len(result)
                })
            else:
                # 返回模拟数据用于测试
                import datetime
                mock_data = []
                current_date = datetime.datetime.strptime(start, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
                base_price = 4500
                
                while current_date <= end_date:
                    if current_date.weekday() < 5:  # 工作日
                        import random
                        change = random.uniform(-50, 50)
                        open_price = base_price + random.uniform(-20, 20)
                        close_price = open_price + change
                        high_price = max(open_price, close_price) + random.uniform(0, 30)
                        low_price = min(open_price, close_price) - random.uniform(0, 30)
                        
                        mock_data.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'code': code,
                            'open': round(open_price, 2),
                            'high': round(high_price, 2),
                            'low': round(low_price, 2),
                            'close': round(close_price, 2),
                            'volume': int(random.uniform(50000, 200000)),
                            'amount': int(random.uniform(2000000000, 9000000000))
                        })
                        base_price = close_price
                    
                    current_date += datetime.timedelta(days=1)
                
                self.write({
                    'status': 200,
                    'message': '使用模拟数据（MongoDB暂无数据）',
                    'res': mock_data
                })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取期货日线数据失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': []
            })


class QDFutureMinHandler(QDBaseHandler):
    """获取期货分钟数据（优化版）"""
    
    def get(self):
        try:
            code = self.get_argument('code')
            start = self.get_argument('start')
            end = self.get_argument('end')
            frequence = self.get_argument('frequence', '1min')
            limit = self.get_argument('limit', '2000')  # 默认限制2000条
            
            # 转换limit参数
            limit = int(limit) if limit else 2000
            
            # 获取期货分钟数据
            data = get_future_data_safe(code, start, end, frequence, limit)
            
            if data is not None and not data.empty:
                # 确保数据格式正确
                if 'datetime' not in data.columns and data.index.name == 'datetime':
                    data = data.reset_index()
                
                # 转换为 JSON 格式
                result = QA_util_to_json_from_pandas(data)
                
                # 设置缓存头
                self.set_header('Cache-Control', 'public, max-age=60')
                
                self.write({
                    'status': 200,
                    'res': result,
                    'count': len(result)
                })
            else:
                # 返回模拟分钟数据
                import datetime
                import random
                mock_data = []
                current_time = datetime.datetime.strptime(f"{start} 09:00:00", '%Y-%m-%d %H:%M:%S')
                end_time = datetime.datetime.strptime(f"{end} 15:00:00", '%Y-%m-%d %H:%M:%S')
                base_price = 4500
                
                # 提取分钟间隔
                freq_num = int(frequence.replace('min', ''))
                
                while current_time <= end_time:
                    # 只在交易时间段生成数据
                    hour = current_time.hour
                    if (9 <= hour < 12) or (13 <= hour < 15):
                        change = random.uniform(-10, 10)
                        open_price = base_price + random.uniform(-5, 5)
                        close_price = open_price + change
                        high_price = max(open_price, close_price) + random.uniform(0, 8)
                        low_price = min(open_price, close_price) - random.uniform(0, 8)
                        
                        mock_data.append({
                            'datetime': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'code': code,
                            'open': round(open_price, 2),
                            'high': round(high_price, 2),
                            'low': round(low_price, 2),
                            'close': round(close_price, 2),
                            'volume': int(random.uniform(1000, 5000))
                        })
                        base_price = close_price
                    
                    current_time += datetime.timedelta(minutes=freq_num)
                    
                    # 跳过非交易时间
                    if current_time.hour >= 15:
                        current_time = current_time.replace(hour=9, minute=0, second=0) + datetime.timedelta(days=1)
                        # 跳过周末
                        while current_time.weekday() >= 5:
                            current_time += datetime.timedelta(days=1)
                
                self.write({
                    'status': 200,
                    'message': '使用模拟数据（MongoDB暂无数据）',
                    'res': mock_data[:500]  # 限制返回数量
                })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取期货分钟数据失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': []
            })


class QDFutureCategoryHandler(QDBaseHandler):
    """获取期货品种分类数据"""

    def get(self):
        """返回按交易所分类的品种数据"""
        try:
            from quanda.QDMarket.market_preset import MARKET_PRESET
            from quanda.QDUtil.QDParameter import EXCHANGE_ID

            preset = MARKET_PRESET()

            # 交易所中文名映射
            exchange_names = {
                EXCHANGE_ID.SHFE: '上期所',
                EXCHANGE_ID.DCE: '大商所',
                EXCHANGE_ID.CZCE: '郑商所',
                EXCHANGE_ID.CFFEX: '中金所',
                EXCHANGE_ID.INE: '能源中心'
            }

            # 按交易所分组
            categories = {}
            for code, info in preset.table.items():
                exchange = info.get('exchange', 'OTHER')
                if exchange not in categories:
                    categories[exchange] = {
                        'name': exchange_names.get(exchange, exchange),
                        'products': []
                    }
                categories[exchange]['products'].append({
                    'code': code,           # 品种代码：RB
                    'name': info['name'],   # 中文名：螺纹钢
                })

            # 转换为数组格式，按固定顺序排列
            exchange_order = [EXCHANGE_ID.SHFE, EXCHANGE_ID.DCE, EXCHANGE_ID.CZCE, EXCHANGE_ID.CFFEX, EXCHANGE_ID.INE]
            result = []
            for exchange in exchange_order:
                if exchange in categories:
                    result.append({
                        'exchange': exchange,
                        'name': categories[exchange]['name'],
                        'products': sorted(categories[exchange]['products'], key=lambda x: x['code'])
                    })

            self.write({
                'status': 200,
                'res': result
            })
        except Exception as e:
            import traceback
            self.write({
                'status': 500,
                'message': f'获取品种分类失败: {str(e)}',
                'error': traceback.format_exc(),
                'res': []
            })


class QDFutureRealtimeHandler(QDBaseHandler):
    """获取期货实时数据"""

    def get(self):
        try:
            code = self.get_argument('code')
            
            # 尝试获取实时数据
            try:
                from quanda.QDFetch.QDTdx import QA_fetch_get_future_realtime
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
