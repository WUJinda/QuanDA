#!/usr/bin/env python3
"""
QADataBridge性能基准测试

对比零拷贝 vs 标准转换的性能差异:
- Pandas ↔ Polars转换性能
- 共享内存 vs 序列化传输
- 不同数据规模的性能表现

生成性能报告，用于评估QADataSwap的加速效果

QuanDA Project
"""

import sys
import time
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

try:
    import polars as pl
    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False
    print("❌ 错误: Polars未安装")
    print("   安装: pip install polars>=0.20.0")
    sys.exit(1)

from quanda.QADataBridge import (
    has_dataswap_support,
    convert_pandas_to_polars,
    convert_polars_to_pandas,
)


# ============================================================================
# 基准测试配置
# ============================================================================

# 测试规模配置
BENCHMARK_CONFIGS = [
    {'rows': 1_000, 'cols': 10, 'name': '小规模'},
    {'rows': 10_000, 'cols': 10, 'name': '中规模'},
    {'rows': 100_000, 'cols': 10, 'name': '大规模'},
    {'rows': 1_000_000, 'cols': 10, 'name': '超大规模'},
]

# 重复测试次数
REPEAT_COUNT = 5


# ============================================================================
# 辅助函数
# ============================================================================

def create_test_dataframe(num_rows: int, num_cols: int) -> pd.DataFrame:
    """
    创建测试用的DataFrame

    参数:
        num_rows: 行数
        num_cols: 列数

    返回:
        pd.DataFrame: 测试数据
    """
    data = {}

    # 浮点列
    for i in range(num_cols // 2):
        data[f'float_col_{i}'] = np.random.rand(num_rows)

    # 整数列
    for i in range(num_cols // 2):
        data[f'int_col_{i}'] = np.random.randint(0, 1000, num_rows)

    return pd.DataFrame(data)


def format_time(milliseconds: float) -> str:
    """
    格式化时间显示

    参数:
        milliseconds: 毫秒

    返回:
        str: 格式化的时间字符串
    """
    if milliseconds < 1:
        return f"{milliseconds * 1000:.2f}μs"
    elif milliseconds < 1000:
        return f"{milliseconds:.2f}ms"
    else:
        return f"{milliseconds / 1000:.2f}s"


def format_size(bytes_size: int) -> str:
    """
    格式化大小显示

    参数:
        bytes_size: 字节数

    返回:
        str: 格式化的大小字符串
    """
    if bytes_size < 1024:
        return f"{bytes_size}B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f}KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f}MB"


# ============================================================================
# Pandas → Polars转换基准测试
# ============================================================================

def benchmark_pandas_to_polars(df: pd.DataFrame, repeat: int = 5) -> dict:
    """
    基准测试: Pandas → Polars转换

    参数:
        df: 测试DataFrame
        repeat: 重复次数

    返回:
        dict: 测试结果
    """
    results = {
        'arrow_times': [],
        'standard_times': [],
    }

    print(f"\n📊 Pandas → Polars转换测试 ({len(df):,}行 x {len(df.columns)}列)")

    # 测试Arrow零拷贝转换
    for i in range(repeat):
        start = time.time()
        df_polars = convert_pandas_to_polars(df)
        elapsed = (time.time() - start) * 1000
        results['arrow_times'].append(elapsed)

    # 测试标准转换
    for i in range(repeat):
        start = time.time()
        df_polars = pl.from_pandas(df)
        elapsed = (time.time() - start) * 1000
        results['standard_times'].append(elapsed)

    # 计算统计
    results['arrow_mean'] = np.mean(results['arrow_times'])
    results['arrow_std'] = np.std(results['arrow_times'])
    results['standard_mean'] = np.mean(results['standard_times'])
    results['standard_std'] = np.std(results['standard_times'])
    results['speedup'] = results['standard_mean'] / results['arrow_mean']

    # 显示结果
    print(f"  Arrow零拷贝: {format_time(results['arrow_mean'])} (±{format_time(results['arrow_std'])})")
    print(f"  标准转换:   {format_time(results['standard_mean'])} (±{format_time(results['standard_std'])})")
    print(f"  加速比:     {results['speedup']:.2f}x")

    if results['speedup'] > 2.0:
        print(f"  ✅ 显著加速 (>{results['speedup']:.1f}x)")
    elif results['speedup'] > 1.2:
        print(f"  ⚡ 中等加速 ({results['speedup']:.1f}x)")
    else:
        print(f"  ➡️  性能相近 (~{results['speedup']:.1f}x)")

    return results


# ============================================================================
# Polars → Pandas转换基准测试
# ============================================================================

def benchmark_polars_to_pandas(df_polars: pl.DataFrame, repeat: int = 5) -> dict:
    """
    基准测试: Polars → Pandas转换

    参数:
        df_polars: 测试DataFrame
        repeat: 重复次数

    返回:
        dict: 测试结果
    """
    results = {
        'arrow_times': [],
        'standard_times': [],
    }

    print(f"\n📊 Polars → Pandas转换测试 ({len(df_polars):,}行 x {len(df_polars.columns)}列)")

    # 测试Arrow零拷贝转换
    for i in range(repeat):
        start = time.time()
        df_pandas = convert_polars_to_pandas(df_polars)
        elapsed = (time.time() - start) * 1000
        results['arrow_times'].append(elapsed)

    # 测试标准转换
    for i in range(repeat):
        start = time.time()
        df_pandas = df_polars.to_pandas()
        elapsed = (time.time() - start) * 1000
        results['standard_times'].append(elapsed)

    # 计算统计
    results['arrow_mean'] = np.mean(results['arrow_times'])
    results['arrow_std'] = np.std(results['arrow_times'])
    results['standard_mean'] = np.mean(results['standard_times'])
    results['standard_std'] = np.std(results['standard_times'])
    results['speedup'] = results['standard_mean'] / results['arrow_mean']

    # 显示结果
    print(f"  Arrow零拷贝: {format_time(results['arrow_mean'])} (±{format_time(results['arrow_std'])})")
    print(f"  标准转换:   {format_time(results['standard_mean'])} (±{format_time(results['standard_std'])})")
    print(f"  加速比:     {results['speedup']:.2f}x")

    return results


# ============================================================================
# 序列化基准测试
# ============================================================================

def benchmark_serialization(df: pd.DataFrame, repeat: int = 5) -> dict:
    """
    基准测试: 序列化 vs 零拷贝

    对比传统pickle序列化和Arrow零拷贝的性能

    参数:
        df: 测试DataFrame
        repeat: 重复次数

    返回:
        dict: 测试结果
    """
    results = {
        'arrow_times': [],
        'pickle_times': [],
    }

    print(f"\n📊 序列化基准测试 ({len(df):,}行 x {len(df.columns)}列)")

    # 测试Arrow转换（模拟零拷贝传输）
    for i in range(repeat):
        start = time.time()
        df_polars = convert_pandas_to_polars(df)
        df_restored = convert_polars_to_pandas(df_polars)
        elapsed = (time.time() - start) * 1000
        results['arrow_times'].append(elapsed)

    # 测试pickle序列化
    for i in range(repeat):
        start = time.time()
        serialized = pickle.dumps(df)
        df_restored = pickle.loads(serialized)
        elapsed = (time.time() - start) * 1000
        results['pickle_times'].append(elapsed)

    # 计算统计
    results['arrow_mean'] = np.mean(results['arrow_times'])
    results['arrow_std'] = np.std(results['arrow_times'])
    results['pickle_mean'] = np.mean(results['pickle_times'])
    results['pickle_std'] = np.std(results['pickle_times'])
    results['speedup'] = results['pickle_mean'] / results['arrow_mean']

    # 计算序列化大小
    serialized = pickle.dumps(df)
    results['pickle_size'] = len(serialized)

    # 显示结果
    print(f"  Arrow零拷贝: {format_time(results['arrow_mean'])} (±{format_time(results['arrow_std'])})")
    print(f"  Pickle序列化: {format_time(results['pickle_mean'])} (±{format_time(results['pickle_std'])})")
    print(f"  Pickle大小:  {format_size(results['pickle_size'])}")
    print(f"  加速比:     {results['speedup']:.2f}x")

    return results


# ============================================================================
# 内存使用基准测试
# ============================================================================

def benchmark_memory_usage(df: pd.DataFrame) -> dict:
    """
    基准测试: 内存使用对比

    参数:
        df: 测试DataFrame

    返回:
        dict: 内存使用结果
    """
    results = {}

    print(f"\n📊 内存使用测试 ({len(df):,}行 x {len(df.columns)}列)")

    # Pandas内存
    pandas_memory = df.memory_usage(deep=True).sum()
    results['pandas_memory'] = pandas_memory

    # Polars内存（估算）
    df_polars = convert_pandas_to_polars(df)
    polars_memory = df_polars.estimated_size()
    results['polars_memory'] = polars_memory

    # Pickle大小
    pickle_size = len(pickle.dumps(df))
    results['pickle_size'] = pickle_size

    # 显示结果
    print(f"  Pandas内存:  {format_size(pandas_memory)}")
    print(f"  Polars内存:  {format_size(polars_memory)}")
    print(f"  Pickle大小:  {format_size(pickle_size)}")
    print(f"  内存节省:   {(1 - polars_memory / pandas_memory) * 100:.1f}%")

    return results


# ============================================================================
# 运行所有基准测试
# ============================================================================

def run_all_benchmarks():
    """运行所有基准测试并生成报告"""
    print("\n" + "=" * 80)
    print("🚀 QADataBridge性能基准测试")
    print("=" * 80)

    # 检查QADataSwap支持
    print(f"\n📦 环境检查:")
    print(f"   QADataSwap: {'✅ 已安装' if has_dataswap_support() else '❌ 未安装'}")
    print(f"   Polars: {'✅ 已安装' if HAS_POLARS else '❌ 未安装'}")

    if not has_dataswap_support():
        print("\n⚠️  警告: QADataSwap未安装，将使用标准转换作为对比")

    # 运行所有配置的测试
    all_results = []

    for config in BENCHMARK_CONFIGS:
        print(f"\n{'=' * 80}")
        print(f"📊 测试配置: {config['name']}")
        print(f"   数据规模: {config['rows']:,}行 x {config['cols']}列")
        print(f"   重复次数: {REPEAT_COUNT}次")
        print(f"{'=' * 80}")

        # 创建测试数据
        df = create_test_dataframe(config['rows'], config['cols'])
        df_polars = convert_pandas_to_polars(df)

        # 运行各项测试
        result = {
            'config': config,
            'pandas_to_polars': benchmark_pandas_to_polars(df, REPEAT_COUNT),
            'polars_to_pandas': benchmark_polars_to_pandas(df_polars, REPEAT_COUNT),
            'serialization': benchmark_serialization(df, REPEAT_COUNT),
            'memory': benchmark_memory_usage(df),
        }

        all_results.append(result)

    # 生成汇总报告
    print_summary_report(all_results)

    return all_results


# ============================================================================
# 打印汇总报告
# ============================================================================

def print_summary_report(results: list):
    """
    打印汇总报告

    参数:
        results: 所有测试结果
    """
    print("\n" + "=" * 80)
    print("📊 性能汇总报告")
    print("=" * 80)

    # 表头
    print(f"\n{'测试规模':<12} {'转换类型':<20} {'Arrow':<15} {'标准':<15} {'加速比':<10}")
    print("-" * 80)

    # 打印每个测试的结果
    for result in results:
        config_name = result['config']['name']

        # Pandas → Polars
        p2p = result['pandas_to_polars']
        print(f"{config_name:<12} {'Pandas→Polars':<20} "
              f"{format_time(p2p['arrow_mean']):<15} "
              f"{format_time(p2p['standard_mean']):<15} "
              f"{p2p['speedup']:.2f}x")

        # Polars → Pandas
        p2pd = result['polars_to_pandas']
        print(f"{'':12} {'Polars→Pandas':<20} "
              f"{format_time(p2pd['arrow_mean']):<15} "
              f"{format_time(p2pd['standard_mean']):<15} "
              f"{p2pd['speedup']:.2f}x")

        # 序列化
        ser = result['serialization']
        print(f"{'':12} {'序列化传输':<20} "
              f"{format_time(ser['arrow_mean']):<15} "
              f"{format_time(ser['pickle_mean']):<15} "
              f"{ser['speedup']:.2f}x")

        print()

    # 内存使用报告
    print("\n" + "=" * 80)
    print("💾 内存使用报告")
    print("=" * 80)

    print(f"\n{'测试规模':<12} {'Pandas':<15} {'Polars':<15} {'Pickle':<15} {'节省率':<10}")
    print("-" * 80)

    for result in results:
        config_name = result['config']['name']
        mem = result['memory']

        pandas_mem = format_size(mem['pandas_memory'])
        polars_mem = format_size(mem['polars_memory'])
        pickle_size = format_size(mem['pickle_size'])
        save_rate = f"{(1 - mem['polars_memory'] / mem['pandas_memory']) * 100:.1f}%"

        print(f"{config_name:<12} {pandas_mem:<15} {polars_mem:<15} {pickle_size:<15} {save_rate:<10}")

    # 总结
    print("\n" + "=" * 80)
    print("✅ 测试结论")
    print("=" * 80)

    avg_speedup_p2p = np.mean([r['pandas_to_polars']['speedup'] for r in results])
    avg_speedup_ser = np.mean([r['serialization']['speedup'] for r in results])

    print(f"\n1. Pandas→Polars平均加速: {avg_speedup_p2p:.2f}x")
    print(f"2. 序列化传输平均加速:   {avg_speedup_ser:.2f}x")
    print(f"3. 内存使用平均节省:     {np.mean([1 - r['memory']['polars_memory'] / r['memory']['pandas_memory'] for r in results]) * 100:.1f}%")

    if has_dataswap_support():
        print("\n✨ QADataSwap零拷贝通信提供了显著的性能提升")
    else:
        print("\n💡 建议安装QADataSwap以获得更好的性能")
        print("   安装: pip install quanda[rust]")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    try:
        results = run_all_benchmarks()

        print("\n" + "=" * 80)
        print("✅ 基准测试完成")
        print("=" * 80)

        print("\n📚 相关信息:")
        print("   - QADataBridge文档: quanda/QADataBridge/README.md")
        print("   - 使用示例: python examples/qadatabridge_example.py")
        print("   - quanda: https://github.com/quanda/quanda")

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
