#!/usr/bin/env python
# coding:utf-8
"""
初始化示例数据（用于测试，不依赖TDX）
"""

from pymongo import MongoClient
from qaenv import mongo_ip
import pandas as pd
from datetime import datetime, timedelta
import random

def get_db():
    """获取数据库连接"""
    client = MongoClient(mongo_ip)
    return client.quantaxis

def init_future_list():
    """初始化期货列表"""
    print("=" * 60)
    print("步骤1: 初始化期货列表")
    print("=" * 60)
    
    db = get_db()
    
    # 常用期货合约
    future_list = [
        {'code': 'IF2403', 'name': '沪深300股指期货2403', 'market': 47},
        {'code': 'IF2404', 'name': '沪深300股指期货2404', 'market': 47},
        {'code': 'IF2406', 'name': '沪深300股指期货2406', 'market': 47},
        {'code': 'IF2409', 'name': '沪深300股指期货2409', 'market': 47},
        {'code': 'IC2403', 'name': '中证500股指期货2403', 'market': 47},
        {'code': 'IC2404', 'name': '中证500股指期货2404', 'market': 47},
        {'code': 'IC2406', 'name': '中证500股指期货2406', 'market': 47},
        {'code': 'IC2409', 'name': '中证500股指期货2409', 'market': 47},
        {'code': 'IH2403', 'name': '上证50股指期货2403', 'market': 47},
        {'code': 'IH2404', 'name': '上证50股指期货2404', 'market': 47},
        {'code': 'IH2406', 'name': '上证50股指期货2406', 'market': 47},
        {'code': 'IH2409', 'name': '上证50股指期货2409', 'market': 47},
    ]
    
    try:
        # 清空旧数据
        db.future_list.delete_many({})
        # 插入新数据
        db.future_list.insert_many(future_list)
        print(f"✓ 成功插入 {len(future_list)} 个期货合约\n")
        return True
    except Exception as e:
        print(f"✗ 插入失败: {e}\n")
        return False


def generate_kline_data(code, start_date, end_date, base_price=3500):
    """生成模拟K线数据"""
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 工作日
    data = []
    
    price = base_price
    for date in dates:
        # 模拟价格波动
        open_price = price + random.uniform(-20, 20)
        close_price = open_price + random.uniform(-30, 30)
        high_price = max(open_price, close_price) + random.uniform(0, 20)
        low_price = min(open_price, close_price) - random.uniform(0, 20)
        volume = random.randint(50000, 200000)
        
        data.append({
            'code': code,
            'date': date.strftime('%Y-%m-%d'),
            'date_stamp': int(date.timestamp()),
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume,
            'amount': round(volume * close_price, 2),
        })
        
        price = close_price  # 下一天的基准价格
    
    return data


def init_future_day_data():
    """初始化期货日线数据"""
    print("=" * 60)
    print("步骤2: 初始化期货日线数据（模拟数据）")
    print("=" * 60)
    
    db = get_db()
    
    # 生成最近3个月的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print("正在生成模拟数据...\n")
    
    codes = ['IF2403', 'IF2404', 'IF2406', 'IC2403', 'IC2404', 'IH2403']
    base_prices = [3500, 3520, 3540, 5800, 5820, 2600]
    
    total_records = 0
    
    try:
        # 清空旧数据
        db.future_day.delete_many({})
        
        for code, base_price in zip(codes, base_prices):
            print(f"  生成 {code} 的数据...")
            data = generate_kline_data(code, start_date, end_date, base_price)
            db.future_day.insert_many(data)
            total_records += len(data)
        
        print(f"\n✓ 成功生成 {total_records} 条K线数据\n")
        return True
    except Exception as e:
        print(f"\n✗ 生成失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("quanda 示例数据初始化")
    print("=" * 60)
    print("注意：这是模拟数据，仅用于测试前端功能")
    print("=" * 60)
    print()
    
    # 检查MongoDB
    try:
        client = MongoClient(mongo_ip)
        client.server_info()
        print("✓ MongoDB连接正常\n")
    except Exception as e:
        print(f"✗ MongoDB连接失败: {e}")
        print("请确保MongoDB服务已启动")
        return
    
    # 初始化期货列表
    if not init_future_list():
        print("初始化失败")
        return
    
    # 初始化期货日线数据
    if not init_future_day_data():
        print("初始化失败")
        return
    
    # 完成
    print("=" * 60)
    print("示例数据初始化完成！")
    print("=" * 60)
    print()
    print("现在可以：")
    print("1. 刷新前端页面")
    print("2. 选择期货品种（IF2403、IC2403等）")
    print("3. 选择日期范围（最近3个月）")
    print("4. 查看K线图")
    print()
    print("前端地址: http://localhost:3000")
    print()
    print("⚠️  注意：这是模拟数据，不是真实行情！")
    print()


if __name__ == '__main__':
    main()
