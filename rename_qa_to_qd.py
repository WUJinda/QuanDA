#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QuanDA 模块重命名脚本: QA 前缀 -> QD 前缀

作者: Claude AI
日期: 2025-03-16

使用方法:
    python rename_qa_to_qd.py

注意:
    - 此脚本会使用 git mv 重命名目录，保持 git 历史
    - 会自动更新所有 Python 文件中的导入语句
    - 会更新 setup.py 配置文件
    - 执行前请确保工作区是干净的 (git status)
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Windows 控制台编码支持
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass


class ModuleRenamer:
    """模块重命名器"""

    # 需要重命名的模块映射
    RENAME_MAP = {
        'QAAnalysis': 'QDAnalysis',
        'QACmd': 'QDCmd',
        'QAData': 'QDData',
        'QADataBridge': 'QDDataBridge',
        'QAEngine': 'QDEngine',
        'QAFactor': 'QDFactor',
        'QAFetch': 'QDFetch',
        'QAIndicator': 'QDIndicator',
        'QAMarket': 'QDMarket',
        'QAPubSub': 'QDPubSub',
        'QARSBridge': 'QDRSBridge',
        'QASchedule': 'QDSchedule',
        'QASetting': 'QDSetting',
        'QAStrategy': 'QDStrategy',
        'QASU': 'QDSU',
        'QAUtil': 'QDUtil',
        'QAWebServer': 'QDWebServer',
        # QIFI 保持不变
    }

    def __init__(self, base_dir='quanda'):
        self.base_dir = Path(base_dir).resolve()
        if not self.base_dir.exists():
            raise FileNotFoundError(f"目录不存在: {self.base_dir}")

    def run_git_command(self, *args):
        """执行 git 命令"""
        cmd = ['git'] + list(args)
        result = subprocess.run(cmd, cwd=self.base_dir.parent,
                              capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Git 命令失败: {' '.join(cmd)}\n{result.stderr}")
        return result

    def check_git_status(self):
        """检查 git 工作区状态"""
        result = self.run_git_command('status', '--porcelain')
        if result.stdout.strip():
            print("[WARNING] 工作区有未提交的更改:")
            print(result.stdout)
            response = input("是否继续? (y/N): ")
            if response.lower() != 'y':
                print("已取消操作")
                sys.exit(1)

    def rename_directories(self):
        """阶段1: 重命名目录"""
        print("\n=== 阶段1: 重命名目录 ===")

        for old_name, new_name in self.RENAME_MAP.items():
            old_path = self.base_dir / old_name
            new_path = self.base_dir / new_name

            if not old_path.exists():
                print(f"[SKIP] {old_name} (目录不存在)")
                continue

            print(f"重命名 {old_name} -> {new_name}")
            try:
                self.run_git_command('mv', str(old_path), str(new_path))
            except RuntimeError as e:
                print(f"[ERROR] 失败: {e}")
                return False

        print("[OK] 目录重命名完成")
        return True

    def update_python_imports(self):
        """阶段2: 更新所有 Python 文件中的导入语句"""
        print("\n=== 阶段2: 更新 Python 文件导入语句 ===")

        updated_count = 0
        skipped_count = 0

        # 遍历所有 .py 文件
        for py_file in self.base_dir.rglob('*.py'):
            # 跳过 __pycache__
            if '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                # 替换导入语句
                for old_name, new_name in self.RENAME_MAP.items():
                    # from quanda.QAXXX
                    content = re.sub(
                        rf'from quanda\.{old_name}\b',
                        f'from quanda.{new_name}',
                        content
                    )
                    # import quanda.QAXXX
                    content = re.sub(
                        rf'import quanda\.{old_name}\b',
                        f'import quanda.{new_name}',
                        content
                    )
                    # from .QAXXX
                    content = re.sub(
                        rf'from \.{old_name}\b',
                        f'from .{new_name}',
                        content
                    )

                # 如果内容有变化，写回文件
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_count += 1
                    if updated_count <= 10:  # 只显示前10个
                        print(f"  更新: {py_file.relative_to(self.base_dir.parent)}")
                else:
                    skipped_count += 1

            except Exception as e:
                print(f"[ERROR] 处理文件 {py_file}: {e}")
                continue

        if updated_count > 10:
            print(f"  ... 还有 {updated_count - 10} 个文件")
        print(f"[OK] 更新了 {updated_count} 个文件，跳过 {skipped_count} 个文件")
        return True

    def update_setup_py(self):
        """阶段3: 更新 setup.py"""
        print("\n=== 阶段3: 更新配置文件 ===")

        setup_py = self.base_dir.parent / 'setup.py'
        if not setup_py.exists():
            print("[SKIP] setup.py 不存在，跳过")
            return True

        try:
            with open(setup_py, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 替换所有模块名
            for old_name, new_name in self.RENAME_MAP.items():
                content = content.replace(old_name, new_name)

            if content != original_content:
                with open(setup_py, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("[OK] setup.py 更新完成")
            else:
                print("[SKIP] setup.py 无需更新")

        except Exception as e:
            print(f"[ERROR] 更新 setup.py 失败: {e}")
            return False

        return True

    def update_readme(self):
        """更新 README.md 中的引用"""
        readme = self.base_dir.parent / 'README.md'
        if not readme.exists():
            return True

        print("\n=== 更新 README.md ===")
        try:
            with open(readme, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 替换所有模块名
            for old_name, new_name in self.RENAME_MAP.items():
                content = content.replace(old_name, new_name)

            if content != original_content:
                with open(readme, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("[OK] README.md 更新完成")

        except Exception as e:
            print(f"[WARNING] 更新 README.md 失败: {e}")

        return True

    def print_summary(self):
        """打印摘要"""
        print("\n" + "="*60)
        print("重命名完成!")
        print("="*60)
        print("\n重命名的目录:")
        for old, new in self.RENAME_MAP.items():
            print(f"  {old} -> {new}")
        print("\n下一步:")
        print("  1. 检查更改: git status")
        print("  2. 查看差异: git diff")
        print("  3. 提交更改: git commit -m '重命名模块: QA 前缀改为 QD 前缀'")
        print("="*60)

    def run(self):
        """执行完整的重命名流程"""
        print("="*60)
        print("QuanDA 模块重命名工具")
        print("QA 前缀 -> QD 前缀")
        print("="*60)

        # 检查 git 状态
        self.check_git_status()

        # 阶段1: 重命名目录
        if not self.rename_directories():
            print("\n[ERROR] 目录重命名失败，中止操作")
            return False

        # 阶段2: 更新导入语句
        if not self.update_python_imports():
            print("\n[ERROR] 更新导入语句失败")
            return False

        # 阶段3: 更新配置文件
        if not self.update_setup_py():
            print("\n[ERROR] 更新配置文件失败")
            return False

        # 更新 README
        self.update_readme()

        # 打印摘要
        self.print_summary()

        return True


def main():
    """主函数"""
    try:
        renamer = ModuleRenamer()
        success = renamer.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
