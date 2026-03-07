#!/usr/bin/env python
# coding:utf-8
"""
期货数据初始化脚本
用于下载期货数据到MongoDB数据库
"""

import quanda as QA
from datetime import datetime, timedelta

def init_future_list():
    """初始化期货列表"""
    print("=" * 60)
    print("开始初始化期货列表...")
    try:
        QA.QA_SU_save_future_list()
        print("✓ 期货列表初始化成功")
        return True
    except Exception as e:
        print(f"✗ 期货列表初始化失败: {e}")
        return False


def init_future_day_data(start_date=None, end_date=None):
    """初始化期货日线数据"""
    print("=" * 60)
    print("开始初始化期货日线数据...")
    
    if start_date is None:
        # 默认获取最近一年的数据
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"时间范围: {start_date} 至 {end_date}")
    
    try:
        QA.QA_SU_save_future_day(start_date, end_date)
        print("✓ 期货日线数据初始化成功")
        return True
    except Exception as e:
        print(f"✗ 期货日线数据初始化失败: {e}")
        return False


def init_future_min_data(start_date=None, end_date=None):
    """初始化期货分钟数据（可选，数据量大）"""
    print("=" * 60)
    print("开始初始化期货分钟数据...")
    print("⚠️  警告：分钟数据量很大，可能需要较长时间")
    
    if start_date is None:
        # 默认获取最近30天的数据
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"时间范围: {start_date} 至 {end_date}")
    
    try:
        QA.QA_SU_save_future_min(start_date, end_date)
        print("✓ 期货分钟数据初始化成功")
        return True
    except Exception as e:
        print(f"✗ 期货分钟数据初始化失败: {e}")
        return False


def check_mongodb_connection():
    """检查MongoDB连接"""
    print("=" * 60)
    print("检查MongoDB连接...")
    try:
        client = QA.DATABASE
        # 尝试获取数据库列表
        client.list_database_names()
        print("✓ MongoDB连接正常")
        return True
    except Exception as e:
        print(f"✗ MongoDB连接失败: {e}")
        print("\n请确保：")
        print("1. MongoDB服务已启动")
        print("2. 配置文件中的MongoDB地址正确")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("quanda 期货数据初始化工具")
    print("=" * 60)
    
    # 检查MongoDB连接
    if not check_mongodb_connection():
        print("\n初始化失败：无法连接到MongoDB")
        return
    
    print("\n请选择要初始化的数据：")
    print("1. 期货列表（必需，< 1MB）")
    print("2. 期货日线数据（推荐，约100-500MB）")
    print("3. 期货分钟数据（可选，数据量大，GB级别）")
    print("4. 全部初始化（列表 + 日线）")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-4): ").strip()
    
    if choice == '1':
        init_future_list()
    elif choice == '2':
        init_future_day_data()
    elif choice == '3':
        init_future_min_data()
    elif choice == '4':
        init_future_list()
        init_future_day_data()
    elif choice == '0':
        print("退出")
        return
    else:
        print("无效选项")
        return
    
    print("\n" + "=" * 60)
    print("初始化完成！")
    print("=" * 60)
    print("\n现在可以启动前端查看数据了：")
    print("cd quantaxis-frontend")
    print("npm run dev")


if __name__ == '__main__':
    main()
