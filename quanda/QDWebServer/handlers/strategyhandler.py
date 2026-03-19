# coding:utf-8
"""
策略管理 API Handler
处理策略的创建、查询、更新、删除等请求
"""
import importlib.util
import json
import os
import re
import sys
import threading
import traceback
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import pymongo
from qaenv import mongo_ip
from tornado.web import RequestHandler
from pydantic import BaseModel, Field


# 全局数据库连接池
_db_client = None
_db_instance = None
_db_lock = threading.Lock()


def get_database():
    """获取数据库连接（单例模式）"""
    global _db_client, _db_instance
    if _db_client is None:
        with _db_lock:
            if _db_client is None:
                _db_client = pymongo.MongoClient(mongo_ip)
                _db_instance = _db_client.quanda
    return _db_instance


def validate_strategy_path(strategy_path: str) -> bool:
    """
    验证策略文件路径是否安全
    防止路径遍历攻击
    """
    if not strategy_path:
        return False

    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    # 规范化路径
    strategy_path_normalized = os.path.normpath(strategy_path)
    project_root_normalized = os.path.normpath(project_root)
    
    # 转换为绝对路径
    if not os.path.isabs(strategy_path_normalized):
        strategy_path_normalized = os.path.abspath(strategy_path_normalized)

    # 检查是否在项目目录内
    try:
        os.path.commonpath([strategy_path_normalized, project_root_normalized])
    except ValueError:
        # 不在同一驱动器或路径
        return False
    
    if not strategy_path_normalized.startswith(project_root_normalized):
        return False

    # 检查是否包含路径遍历
    if '..' in strategy_path:
        return False

    # 检查文件扩展名
    if not strategy_path.endswith('.py'):
        return False

    return True


class StrategyParams(BaseModel):
    """策略参数基类 - 供前端动态生成表单使用"""
    pass


class StrategyHandler(RequestHandler):
    """策略管理基础类"""

    def initialize(self):
        """初始化数据库连接"""
        self.database = get_database()
        self.collection = self.database.strategies


class StrategyListHandler(StrategyHandler):
    """获取策略列表"""

    def get(self):
        """GET /api/strategy/list"""
        try:
            # 分页参数
            skip = int(self.get_argument('skip', 0))
            limit = int(self.get_argument('limit', 20))
            status = self.get_argument('status', None)
            strategy_type = self.get_argument('type', None)
            keyword = self.get_argument('keyword', None)

            # 构建查询条件
            query = {}
            if status:
                query['status'] = status
            if strategy_type:
                query['type'] = strategy_type
            if keyword:
                query['$or'] = [
                    {'name': {'$regex': keyword, '$options': 'i'}},
                    {'description': {'$regex': keyword, '$options': 'i'}}
                ]

            # 查询
            total = self.collection.count_documents(query)
            strategies = list(self.collection.find(
                query,
                {'_id': 0, 'code': 0}  # 排除代码内容
            ).sort('create_time', -1).skip(skip).limit(limit))

            self.write({
                'status': 200,
                'message': '获取成功',
                'res': {
                    'total': total,
                    'list': strategies,
                    'skip': skip,
                    'limit': limit
                }
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class StrategyDetailHandler(StrategyHandler):
    """获取策略详情"""

    def get(self, strategy_id: str):
        """GET /api/strategy/:id"""
        try:
            strategy = self.collection.find_one(
                {'id': strategy_id},
                {'_id': 0}
            )

            if not strategy:
                self.write({
                    'status': 404,
                    'message': '策略不存在',
                    'res': None
                })
                return

            self.write({
                'status': 200,
                'message': '获取成功',
                'res': strategy
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class StrategyCreateHandler(StrategyHandler):
    """创建策略"""

    def post(self):
        """POST /api/strategy/create"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))

            name = data.get('name')
            strategy_type = data.get('type', 'custom')
            description = data.get('description', '')
            code = data.get('code', '')
            parameters = data.get('parameters', {})
            tags = data.get('tags', [])

            if not name:
                self.write({
                    'status': 400,
                    'message': '策略名称不能为空',
                    'res': None
                })
                return

            # 生成策略ID
            strategy_id = str(uuid.uuid4())

            # 创建策略记录
            strategy = {
                'id': strategy_id,
                'name': name,
                'type': strategy_type,
                'description': description,
                'file_path': '',
                'code': code,
                'status': 'stopped',
                'parameters': parameters,
                'tags': tags,
                'profit': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'create_time': datetime.now().isoformat(),
                'update_time': datetime.now().isoformat(),
            }

            self.collection.insert_one(strategy)

            # 返回时不包含代码
            result = {k: v for k, v in strategy.items() if k != 'code'}

            self.write({
                'status': 200,
                'message': '策略创建成功',
                'res': result
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class StrategyUpdateHandler(StrategyHandler):
    """更新策略"""

    def put(self, strategy_id: str):
        """PUT /api/strategy/:id"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))

            # 检查策略是否存在
            existing = self.collection.find_one({'id': strategy_id})
            if not existing:
                self.write({
                    'status': 404,
                    'message': '策略不存在',
                    'res': None
                })
                return

            # 更新字段
            update_data = {'update_time': datetime.now().isoformat()}

            if 'name' in data:
                update_data['name'] = data['name']
            if 'type' in data:
                update_data['type'] = data['type']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'code' in data:
                update_data['code'] = data['code']
            if 'parameters' in data:
                update_data['parameters'] = data['parameters']
            if 'tags' in data:
                update_data['tags'] = data['tags']

            self.collection.update_one(
                {'id': strategy_id},
                {'$set': update_data}
            )

            # 获取更新后的策略
            updated = self.collection.find_one(
                {'id': strategy_id},
                {'_id': 0}
            )

            self.write({
                'status': 200,
                'message': '策略更新成功',
                'res': updated
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class StrategyDeleteHandler(StrategyHandler):
    """删除策略"""

    def delete(self, strategy_id: str):
        """DELETE /api/strategy/:id"""
        try:
            # 检查策略是否存在
            existing = self.collection.find_one({'id': strategy_id})
            if not existing:
                self.write({
                    'status': 404,
                    'message': '策略不存在',
                    'res': None
                })
                return

            # 检查策略是否正在运行
            if existing.get('status') == 'running':
                self.write({
                    'status': 400,
                    'message': '策略正在运行中，请先停止',
                    'res': None
                })
                return

            # 删除策略
            self.collection.delete_one({'id': strategy_id})

            self.write({
                'status': 200,
                'message': '策略删除成功',
                'res': None
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class StrategyStartHandler(StrategyHandler):
    """启动策略"""

    def post(self, strategy_id: str):
        """POST /api/strategy/:id/start"""
        try:
            # 检查策略是否存在
            strategy = self.collection.find_one({'id': strategy_id})
            if not strategy:
                self.write({
                    'status': 404,
                    'message': '策略不存在',
                    'res': None
                })
                return

            # 检查策略状态
            if strategy.get('status') == 'running':
                self.write({
                    'status': 400,
                    'message': '策略已在运行中',
                    'res': None
                })
                return

            # TODO: 实际启动策略的逻辑（需要根据实盘/模拟模式实现）

            # 更新状态
            self.collection.update_one(
                {'id': strategy_id},
                {'$set': {
                    'status': 'running',
                    'start_time': datetime.now().isoformat()
                }}
            )

            self.write({
                'status': 200,
                'message': '策略启动成功',
                'res': {'strategy_id': strategy_id, 'status': 'running'}
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class StrategyStopHandler(StrategyHandler):
    """停止策略"""

    def post(self, strategy_id: str):
        """POST /api/strategy/:id/stop"""
        try:
            # 检查策略是否存在
            strategy = self.collection.find_one({'id': strategy_id})
            if not strategy:
                self.write({
                    'status': 404,
                    'message': '策略不存在',
                    'res': None
                })
                return

            # 检查策略状态
            if strategy.get('status') != 'running':
                self.write({
                    'status': 400,
                    'message': '策略未在运行',
                    'res': None
                })
                return

            # TODO: 实际停止策略的逻辑

            # 更新状态
            self.collection.update_one(
                {'id': strategy_id},
                {'$set': {
                    'status': 'stopped',
                    'stop_time': datetime.now().isoformat()
                }}
            )

            self.write({
                'status': 200,
                'message': '策略停止成功',
                'res': {'strategy_id': strategy_id, 'status': 'stopped'}
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class StrategyAnalyzeHandler(StrategyHandler):
    """分析策略代码，提取参数"""

    def post(self):
        """POST /api/strategy/analyze"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            code = data.get('code', '')

            if not code:
                self.write({
                    'status': 400,
                    'message': '代码不能为空',
                    'res': None
                })
                return

            # 分析代码提取参数
            parameters = self._extract_parameters(code)
            strategy_class = self._extract_strategy_class(code)

            self.write({
                'status': 200,
                'message': '分析成功',
                'res': {
                    'parameters': parameters,
                    'strategy_class': strategy_class
                }
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })

    def _extract_parameters(self, code: str) -> List[Dict]:
        """从代码中提取参数定义"""
        parameters = []

        # 查找 Pydantic 参数类
        param_pattern = r'class\s+(\w*Params?)\s*\([^)]*BaseModel[^)]*\):\s*"""([^"]*)"""(.*?)(?=\nclass|\Z)'
        matches = re.findall(param_pattern, code, re.DOTALL)

        for match in matches:
            class_name, docstring, body = match

            # 提取字段定义
            field_pattern = r'(\w+):\s*(\w+)\s*=\s*Field\([^)]*default\s*=\s*([^,)]+)[^)]*title\s*=\s*"([^"]+)"'
            fields = re.findall(field_pattern, body)

            for field_name, field_type, default_value, title in fields:
                param = {
                    'name': field_name,
                    'type': field_type,
                    'default': self._parse_default_value(default_value, field_type),
                    'title': title,
                    'description': docstring.strip() if docstring else ''
                }
                parameters.append(param)

        return parameters

    def _extract_strategy_class(self, code: str) -> Optional[str]:
        """提取策略类名"""
        pattern = r'class\s+(\w+)\s*\([^)]*QAStrategyCtaBase[^)]*\)'
        match = re.search(pattern, code)
        if match:
            return match.group(1)
        return None

    def _parse_default_value(self, value: str, value_type: str):
        """解析默认值"""
        value = value.strip()

        try:
            if value_type in ('int', 'float'):
                return float(value) if '.' in value else int(value)
            elif value_type == 'bool':
                return value.lower() == 'true'
            elif value_type == 'str':
                return value.strip('"\'')
            else:
                return value
        except:
            return value


class StrategyCodeHandler(StrategyHandler):
    """获取/更新策略代码"""

    def get(self, strategy_id: str):
        """GET /api/strategy/:id/code"""
        try:
            strategy = self.collection.find_one(
                {'id': strategy_id},
                {'_id': 0, 'code': 1, 'name': 1}
            )

            if not strategy:
                self.write({
                    'status': 404,
                    'message': '策略不存在',
                    'res': None
                })
                return

            self.write({
                'status': 200,
                'message': '获取成功',
                'res': {
                    'code': strategy.get('code', ''),
                    'name': strategy.get('name', '')
                }
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })

    def put(self, strategy_id: str):
        """PUT /api/strategy/:id/code"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            code = data.get('code', '')

            # 检查策略是否存在
            existing = self.collection.find_one({'id': strategy_id})
            if not existing:
                self.write({
                    'status': 404,
                    'message': '策略不存在',
                    'res': None
                })
                return

            # 更新代码
            self.collection.update_one(
                {'id': strategy_id},
                {'$set': {
                    'code': code,
                    'update_time': datetime.now().isoformat()
                }}
            )

            self.write({
                'status': 200,
                'message': '代码更新成功',
                'res': None
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })
