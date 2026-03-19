# coding:utf-8
"""
运行所有回测系统测试
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "回测系统完整测试套件" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # 运行安全性测试
    print("🔒 运行安全性测试...")
    print("-" * 80)
    try:
        from test_backtest_security import main as security_test
        security_test()
    except Exception as e:
        print(f"❌ 安全性测试失败: {e}")
    
    print("\n")
    
    # 运行性能测试
    print("⚡ 运行性能测试...")
    print("-" * 80)
    try:
        from test_backtest_performance import main as performance_test
        performance_test()
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
    
    print("\n")
    print("=" * 80)
    print("✅ 所有测试完成!")
    print("=" * 80)
    print()
    print("📊 测试报告:")
    print("   - 安全性测试: 查看上方输出")
    print("   - 性能测试: 查看上方输出")
    print()
    print("📖 详细文档:")
    print("   - 优化建议: changelogs/backtest_review_recommendations.md")
    print("   - 优化总结: changelogs/backtest_optimization_summary.md")
    print("   - 使用指南: changelogs/BACKTEST_OPTIMIZATION_GUIDE.md")
    print("   - 完成报告: changelogs/OPTIMIZATION_COMPLETE.md")
    print()


if __name__ == '__main__':
    main()
