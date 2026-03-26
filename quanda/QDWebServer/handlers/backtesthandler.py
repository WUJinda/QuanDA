# coding:utf-8
"""
回测系统 API Handler
处理回测任务的创建、执行、查询等请求
"""
import asyncio
import json
import logging
import threading
import time
import traceback
from datetime import datetime
from typing import Dict, List

import tornado.websocket
from tornado.web import RequestHandler
from pydantic import ValidationError

from quanda.QDSU.backtest_runner import backtest_manager, BacktestRunner
from quanda.QDSU.backtest_models import BacktestConfig

# 配置日志
logger = logging.getLogger(__name__)


class BacktestListHandler(RequestHandler):
    """获取回测任务列表"""

    def get(self):
        """GET /api/backtest/list"""
        try:
            skip = int(self.get_argument('skip', 0))
            limit = int(self.get_argument('limit', 20))

            tasks = backtest_manager.list_backtests(skip, limit)
            total = backtest_manager.count_backtests()

            self.write({
                'status': 200,
                'message': '获取成功',
                'res': {
                    'list': tasks,
                    'total': total,
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


class BacktestCreateHandler(RequestHandler):
    """创建回测任务"""

    def post(self):
        """POST /api/backtest/create"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))

            # 使用 Pydantic 验证参数
            try:
                config = BacktestConfig(**data)
            except ValidationError as e:
                logger.warning(f"参数验证失败: {e}")
                self.write({
                    'status': 400,
                    'message': f'参数验证失败: {e.errors()[0]["msg"]}',
                    'res': None
                })
                return

            backtest_id = backtest_manager.create_backtest(
                strategy_path=config.strategy_path,
                strategy_class_name=config.strategy_class_name,
                start_date=config.start_date,
                end_date=config.end_date,
                init_cash=config.init_cash,
                code=config.code,
                frequence=config.frequence
            )

            logger.info(f"回测任务创建成功: {backtest_id}")
            self.write({
                'status': 200,
                'message': '回测任务创建成功',
                'res': {'backtest_id': backtest_id}
            })
        except Exception as e:
            logger.exception(f"创建回测任务失败: {e}")
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class BacktestDetailHandler(RequestHandler):
    """获取回测任务详情"""

    def get(self, backtest_id: str):
        """GET /api/backtest/:id"""
        try:
            task = backtest_manager.get_backtest_status(backtest_id)

            if not task:
                self.write({
                    'status': 404,
                    'message': '回测任务不存在',
                    'res': None
                })
                return

            self.write({
                'status': 200,
                'message': '获取成功',
                'res': task
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class BacktestResultHandler(RequestHandler):
    """获取回测结果"""

    def get(self, backtest_id: str):
        """GET /api/backtest/result/:id"""
        try:
            result = backtest_manager.get_backtest_result(backtest_id)

            if not result:
                self.write({
                    'status': 404,
                    'message': '回测结果不存在',
                    'res': None
                })
                return

            self.write({
                'status': 200,
                'message': '获取成功',
                'res': result
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class BacktestRunHandler(RequestHandler):
    """运行回测任务"""

    def post(self, backtest_id: str):
        """POST /api/backtest/run/:id"""
        try:
            # 检查任务是否存在
            task = backtest_manager.get_backtest_status(backtest_id)
            if not task:
                self.write({
                    'status': 404,
                    'message': '回测任务不存在',
                    'res': None
                })
                return

            if task.get('status') == 'running':
                self.write({
                    'status': 400,
                    'message': '回测任务正在运行中',
                    'res': None
                })
                return

            # 创建并启动回测
            runner = backtest_manager.start_backtest(backtest_id)

            # 在后台线程执行回测
            def run_backtest():
                try:
                    runner.run()
                except Exception as e:
                    print(f"回测执行错误: {e}")

            thread = threading.Thread(target=run_backtest, daemon=True)
            thread.start()

            self.write({
                'status': 200,
                'message': '回测任务已启动',
                'res': {'backtest_id': backtest_id}
            })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class BacktestDeleteHandler(RequestHandler):
    """删除回测任务"""

    def delete(self, backtest_id: str):
        """DELETE /api/backtest/:id"""
        try:
            success = backtest_manager.delete_backtest(backtest_id)

            if success:
                self.write({
                    'status': 200,
                    'message': '删除成功',
                    'res': None
                })
            else:
                self.write({
                    'status': 404,
                    'message': '回测任务不存在',
                    'res': None
                })
        except Exception as e:
            traceback.print_exc()
            self.write({
                'status': 500,
                'message': str(e),
                'res': None
            })


class BacktestWebSocketHandler(tornado.websocket.WebSocketHandler):
    """WebSocket 实时回测进度推送（带心跳检测）"""

    clients: Dict[str, List['BacktestWebSocketHandler']] = {}
    _clients_lock = threading.Lock()  # 线程安全锁

    def check_origin(self, origin):
        """允许跨域"""
        return True

    def open(self, backtest_id: str):
        """WebSocket 连接打开"""
        self.backtest_id = backtest_id
        self.last_ping = time.time()
        self.is_alive = True

        with BacktestWebSocketHandler._clients_lock:
            if backtest_id not in BacktestWebSocketHandler.clients:
                BacktestWebSocketHandler.clients[backtest_id] = []
            BacktestWebSocketHandler.clients[backtest_id].append(self)

        print(f"WebSocket 连接已建立: {backtest_id}")

        # 启动心跳检测
        self.ping_callback = tornado.ioloop.PeriodicCallback(
            self.send_ping, 30000  # 30秒
        )
        self.ping_callback.start()

        # 检查任务状态并发送当前状态
        task = backtest_manager.get_backtest_status(backtest_id)
        if task:
            self.send_message({
                'type': 'status',
                'data': task
            })

    def send_ping(self):
        """发送心跳包"""
        try:
            if not self.is_alive:
                return
            
            self.ping(b'')
            
            # 检查超时（90秒无响应）
            if time.time() - self.last_ping > 90:
                print(f"WebSocket 连接超时，关闭连接: {self.backtest_id}")
                self.close()
        except Exception as e:
            print(f"发送心跳失败: {e}")
            self.close()

    def on_pong(self, data):
        """收到 pong 响应"""
        self.last_ping = time.time()

    def on_close(self):
        """WebSocket 连接关闭"""
        self.is_alive = False
        
        # 停止心跳检测
        if hasattr(self, 'ping_callback'):
            self.ping_callback.stop()
        
        with BacktestWebSocketHandler._clients_lock:
            if self.backtest_id in BacktestWebSocketHandler.clients:
                if self in BacktestWebSocketHandler.clients[self.backtest_id]:
                    BacktestWebSocketHandler.clients[self.backtest_id].remove(self)
                
                # 如果没有客户端了，清理字典
                if not BacktestWebSocketHandler.clients[self.backtest_id]:
                    del BacktestWebSocketHandler.clients[self.backtest_id]

        print(f"WebSocket 连接已关闭: {self.backtest_id}")

    def on_message(self, message):
        """接收消息"""
        try:
            data = json.loads(message)
            action = data.get('action')

            if action == 'start':
                # 启动回测
                self.start_backtest()
            elif action == 'get_status':
                # 获取状态
                task = backtest_manager.get_backtest_status(self.backtest_id)
                if task:
                    self.send_message({
                        'type': 'status',
                        'data': task
                    })

        except Exception as e:
            traceback.print_exc()
            self.send_message({
                'type': 'error',
                'message': str(e)
            })

    def start_backtest(self):
        """启动回测"""
        task = backtest_manager.get_backtest_status(self.backtest_id)
        if not task:
            self.send_message({
                'type': 'error',
                'message': '回测任务不存在'
            })
            return

        if task.get('status') == 'running':
            self.send_message({
                'type': 'error',
                'message': '回测任务正在运行中'
            })
            return

        def progress_callback(progress: int, message: str):
            """进度回调"""
            self.broadcast_progress(self.backtest_id, progress, message)

        def ws_callback(data: dict):
            """WebSocket数据推送回调"""
            self.broadcast_data(self.backtest_id, data)

        try:
            runner = backtest_manager.start_backtest(
                self.backtest_id,
                progress_callback=progress_callback,
                ws_callback=ws_callback
            )

            def run_backtest():
                try:
                    result = runner.run()
                    # 发送完成消息
                    self.broadcast_result(self.backtest_id, result)
                except Exception as e:
                    self.broadcast_error(self.backtest_id, str(e))

            thread = threading.Thread(target=run_backtest, daemon=True)
            thread.start()

            self.send_message({
                'type': 'started',
                'message': '回测任务已启动'
            })

        except Exception as e:
            traceback.print_exc()
            self.send_message({
                'type': 'error',
                'message': str(e)
            })

    def send_message(self, data: dict):
        """发送消息"""
        try:
            self.write_message(json.dumps(data, ensure_ascii=False))
        except:
            pass

    @classmethod
    def broadcast_progress(cls, backtest_id: str, progress: int, message: str):
        """广播进度"""
        with cls._clients_lock:
            clients = cls.clients.get(backtest_id, []).copy()

        data = {
            'type': 'progress',
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        for client in clients:
            try:
                client.write_message(json.dumps(data, ensure_ascii=False))
            except:
                pass

    @classmethod
    def broadcast_result(cls, backtest_id: str, result: dict):
        """广播结果"""
        with cls._clients_lock:
            clients = cls.clients.get(backtest_id, []).copy()

        data = {
            'type': 'completed',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        for client in clients:
            try:
                client.write_message(json.dumps(data, ensure_ascii=False))
            except:
                pass

    @classmethod
    def broadcast_error(cls, backtest_id: str, error: str):
        """广播错误"""
        with cls._clients_lock:
            clients = cls.clients.get(backtest_id, []).copy()

        data = {
            'type': 'error',
            'message': error,
            'timestamp': datetime.now().isoformat()
        }
        for client in clients:
            try:
                client.write_message(json.dumps(data, ensure_ascii=False))
            except:
                pass

    @classmethod
    def broadcast_data(cls, backtest_id: str, data: dict):
        """广播数据（K线、账户状态等）"""
        with cls._clients_lock:
            clients = cls.clients.get(backtest_id, []).copy()

        # 添加时间戳
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()

        message = json.dumps(data, ensure_ascii=False)
        for client in clients:
            try:
                client.write_message(message)
            except:
                pass
