#!/usr/bin/env python
# coding:utf-8
"""
自动初始化期货数据（无需交互）
"""

import quanda as QA
from datetime import datetime, timedelta
import sys

def check_mongodb():
    """检查MongoDB连接"""
    print("检查MongoDB连接...")
    try:
        from pymongo import MongoClient
        from qaenv import mongo_ip
        client = MongoClient(mongo_ip)
        # 测试连接
        client.server_info()
        print("✓ MongoDB连接正常\n")
        return True
    except Exception as e:
        print(f"✗ MongoDB连接失败: {e}\n")
        return False


def init_future_list():
    """初始化期货列表"""
    print("=" * 60)
    print("步骤1: 初始化期货列表")
    print("=" * 60)
    try:
        from quanda.QASU.save_tdx import QA_SU_save_future_list
        QA_SU_save_future_list()
        print("✓ 期货列表初始化成功\n")
        return True
    except Exception as e:
        print(f"✗ 期货列表初始化失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def init_future_day():
    """初始化期货日线数据（最近一年）"""
    print("=" * 60)
    print("步骤2: 初始化期货日线数据")
    print("=" * 60)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"时间范围: {start_date} 至 {end_date}")
    print("预计需要: 5-15分钟")
    print("正在下载数据，请耐心等待...\n")
    
    try:
        from quanda.QASU.save_tdx import QA_SU_save_future_day
        QA_SU_save_future_day(start_date, end_date)
        print("\n✓ 期货日线数据初始化成功\n")
        return True
    except Exception as e:
        print(f"\n✗ 期货日线数据初始化失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("quanda 期货数据自动初始化")
    print("=" * 60)
    print()
    
    # 检查MongoDB
    if not check_mongodb():
        print("初始化失败：无法连接到MongoDB")
        print("请确保MongoDB服务已启动")
        sys.exit(1)
    
    # 初始化期货列表
    if not init_future_list():
        print("初始化失败：无法保存期货列表")
        sys.exit(1)
    
    # 初始化期货日线数据
    if not init_future_day():
        print("初始化失败：无法保存期货日线数据")
        sys.exit(1)
    
    # 完成
    print("=" * 60)
    print("数据初始化完成！")
    print("=" * 60)
    print()
    print("现在可以：")
    print("1. 刷新前端页面")
    print("2. 选择期货品种")
    print("3. 查看K线图")
    print()
    print("前端地址: http://localhost:3000")
    print()


if __name__ == '__main__':
    main()
