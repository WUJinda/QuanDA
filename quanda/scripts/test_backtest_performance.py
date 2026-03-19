# coding:utf-8
"""
回测系统性能测试脚本
测试内存占用、并发性能等
"""
import sys
import os
import time
import threading
import psutil

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from quanda.QDSU.backtest_runner import BacktestManager


def get_memory_usage():
    """获取当前进程内存占用（MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def test_memory_optimization():
    """测试内存优化效果"""
    print("=" * 60)
    print("测试 1: 内存优化效果")
    print("=" * 60)
    
    initial_memory = get_memory_usage()
    print(f"初始内存占用: {initial_memory:.2f} MB")
    
    # 模拟大量账户历史记录
    account_history = []
    for i in range(100000):
        account_history.append({
            'datetime': f'2024-01-01 {i:06d}',
            'balance': 100000 + i,
            'available': 100000,
            'margin': 0,
            'float_profit': 0,
            'close_profit': 0,
        })
    
    after_creation = get_memory_usage()
    print(f"创建10万条记录后: {after_creation:.2f} MB")
    print(f"内存增长: {after_creation - initial_memory:.2f} MB")
    
    # 清理
    account_history = []
    
    after_cleanup = get_memory_usage()
    print(f"清理后: {after_cleanup:.2f} MB")
    print(f"释放内存: {after_creation - after_cleanup:.2f} MB")
    
    print()


def test_concurrent_tasks():
    """测试并发任务处理"""
    print("=" * 60)
    print("测试 2: 并发任务处理")
    print("=" * 60)
    
    manager = BacktestManager()
    
    # 创建多个回测任务
    task_ids = []
    for i in range(5):
        task_id = manager.create_backtest(
            strategy_path=f'test_strategy_{i}.py',
            start_date='2024-01-01',
            end_date='2024-01-31',
            init_cash=100000
        )
        task_ids.append(task_id)
        print(f"✅ 创建任务 {i+1}: {task_id}")
    
    # 测试并发访问
    def access_task(task_id):
        for _ in range(100):
            status = manager.get_backtest_status(task_id)
            if status:
                pass  # 模拟处理
    
    threads = []
    start_time = time.time()
    
    for task_id in task_ids:
        thread = threading.Thread(target=access_task, args=(task_id,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    elapsed = time.time() - start_time
    print(f"✅ 并发访问完成: {elapsed:.2f}秒")
    print(f"   总请求数: {5 * 100} 次")
    print(f"   平均响应时间: {elapsed / 500 * 1000:.2f}ms")
    
    # 清理
    for task_id in task_ids:
        manager.delete_backtest(task_id)
    
    print()


def test_database_connection_pool():
    """测试数据库连接池"""
    print("=" * 60)
    print("测试 3: 数据库连接池")
    print("=" * 60)
    
    from quanda.QDSU.backtest_runner import get_database
    
    # 多次获取数据库连接
    connections = []
    start_time = time.time()
    
    for i in range(100):
        db = get_database()
        connections.append(db)
    
    elapsed = time.time() - start_time
    
    print(f"✅ 获取100个连接耗时: {elapsed:.3f}秒")
    print(f"   平均每次: {elapsed / 100 * 1000:.2f}ms")
    
    # 验证连接复用
    unique_connections = len(set(id(conn) for conn in connections))
    print(f"   唯一连接数: {unique_connections}")
    print(f"   连接复用率: {(100 - unique_connections) / 100 * 100:.1f}%")
    
    print()


def test_sampling_efficiency():
    """测试采样记录效率"""
    print("=" * 60)
    print("测试 4: 采样记录效率")
    print("=" * 60)
    
    # 模拟不采样
    start_time = time.time()
    full_history = []
    for i in range(100000):
        full_history.append({
            'datetime': f'2024-01-01 {i:06d}',
            'balance': 100000 + i,
        })
    full_time = time.time() - start_time
    full_memory = sys.getsizeof(full_history) / 1024 / 1024
    
    print(f"不采样 (10万条):")
    print(f"   耗时: {full_time:.3f}秒")
    print(f"   内存: {full_memory:.2f} MB")
    
    # 模拟采样（每10条记录1条）
    start_time = time.time()
    sampled_history = []
    for i in range(100000):
        if i % 10 == 0:
            sampled_history.append({
                'datetime': f'2024-01-01 {i:06d}',
                'balance': 100000 + i,
            })
    sampled_time = time.time() - start_time
    sampled_memory = sys.getsizeof(sampled_history) / 1024 / 1024
    
    print(f"\n采样记录 (1万条):")
    print(f"   耗时: {sampled_time:.3f}秒")
    print(f"   内存: {sampled_memory:.2f} MB")
    
    print(f"\n优化效果:")
    print(f"   时间节省: {(1 - sampled_time / full_time) * 100:.1f}%")
    print(f"   内存节省: {(1 - sampled_memory / full_memory) * 100:.1f}%")
    
    print()


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "回测系统性能测试" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    test_memory_optimization()
    test_concurrent_tasks()
    test_database_connection_pool()
    test_sampling_efficiency()
    
    print("=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
