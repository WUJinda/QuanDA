#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QuanDA Python 后端构建脚本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """构建 Python 后端"""
    print("=" * 50)
    print("QuanDA Python 后端构建")
    print("=" * 50)

    # 获取目录
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    dist_dir = backend_dir / 'dist'

    # 清理旧的构建
    if dist_dir.exists():
        print(f"清理旧构建: {dist_dir}")
        shutil.rmtree(dist_dir)

    # 创建构建目录
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 检查 PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("错误: PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        sys.exit(1)

    # 运行 PyInstaller
    print("\n开始打包...")
    config_file = backend_dir / 'pyinstaller.config.py'

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        str(config_file),
        '--clean',
        '--distpath', str(dist_dir),
        '--workpath', str(backend_dir / 'build'),
    ]

    print(f"运行命令: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print("\n构建完成!")
        print(f"输出目录: {dist_dir}")

        # 检查输出
        exe_file = dist_dir / 'quanda-backend.exe'
        if exe_file.exists():
            print(f"可执行文件: {exe_file}")
            print(f"文件大小: {exe_file.stat().st_size / 1024 / 1024:.2f} MB")

    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
