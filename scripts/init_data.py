#!/usr/bin/env python
# coding:utf-8
"""
quanda 数据初始化脚本
用于初始化期货、股票等市场数据到 MongoDB
"""

import quanda as QA
from datetime import datetime, timedelta

def init_future_data():
    """初始化期货数据"""
    print("="*60)
    print("开始初始化期货数据...")
    print("="*60)
    
    try:
        # 1. 保存期货列表
        print("\n1. 保存期货列表...")
        QA.QA_SU_save_future_list()
        print("✅ 期货列表保存完成")
        
        # 2. 保存期货日线数据（最近一年）
        print("\n2. 保存期货日线数据（最近一年）...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        print(f"   日期范围: {start_date} 到 {end_date}")
        QA.QA_SU_save_future_day(start=start_date, end=end_date)
        print("✅ 期货日线数据保存完成")
        
        # 3. 保存期货分钟数据（可选，数据量大）
        print("\n3. 期货分钟数据...")
        print("   ⚠️  分钟数据量较大，建议按需保存")
        print("   如需保存，请取消注释以下代码：")
        print("   # QA.QA_SU_save_future_min()")
        
        print("\n" + "="*60)
        print("✅ 数据初始化完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()

def update_future_data(days=7):
    """更新期货数据"""
    print("="*60)
    print(f"更新最近 {days} 天的期货数据...")
    print("="*60)
    
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"日期范围: {start_date} 到 {end_date}")
        QA.QA_SU_save_future_day(start=start_date, end=end_date)
        
        print("\n✅ 数据更新完成！")
        
    except Exception as e:
        print(f"\n❌ 更新失败: {str(e)}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'update':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            update_future_data(days)
        else:
            print("用法:")
            print("  python init_data.py          # 初始化数据")
            print("  python init_data.py update   # 更新最近7天数据")
            print("  python init_data.py update 30 # 更新最近30天数据")
    else:
        init_future_data()
