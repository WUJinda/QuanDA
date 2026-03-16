#!/bin/bash
# QuanDA 模块重命名脚本: QA 前缀 -> QD 前缀
# 作者: Claude AI
# 日期: 2025-03-16

set -e  # 遇到错误立即退出

cd quanda

echo "=== 阶段1: 重命名目录 ==="

# 使用 git mv 保持 git 历史
git mv QAAnalysis QDAnalysis
git mv QACmd QDCmd
git mv QAData QDData
git mv QADataBridge QDDataBridge
git mv QAEngine QDEngine
git mv QAFactor QDFactor
git mv QAFetch QDFetch
git mv QAIndicator QDIndicator
git mv QAMarket QDMarket
git mv QAPubSub QDPubSub
git mv QARSBridge QDRSBridge
git mv QASchedule QDSchedule
git mv QASetting QDSetting
git mv QAStrategy QDStrategy
git mv QASU QDSU
git mv QAUtil QDUtil
git mv QAWebServer QDWebServer

echo "✓ 目录重命名完成"
echo ""
echo "=== 阶段2: 更新所有 Python 文件中的导入语句 ==="

# 查找所有 .py 文件并替换导入语句
find . -name "*.py" -type f -exec sed -i 's/from quanda\.QA\([A-Z]\)/from quanda.QD\1/g' {} \;
find . -name "*.py" -type f -exec sed -i 's/import quanda\.QA\([A-Z]\)/import quanda.QD\1/g' {} \;
find . -name "*.py" -type f -exec sed -i 's/from \.QA\([A-Z]\)/from .QD\1/g' {} \;

echo "✓ Python 文件导入语句更新完成"
echo ""
echo "=== 阶段3: 更新配置文件 ==="

# 更新 setup.py (如果存在)
if [ -f "../setup.py" ]; then
    sed -i 's/QAAnalysis/QDAnalysis/g' ../setup.py
    sed -i 's/QACmd/QDCmd/g' ../setup.py
    sed -i 's/QAData/QDData/g' ../setup.py
    sed -i 's/QADataBridge/QDDataBridge/g' ../setup.py
    sed -i 's/QAEngine/QDEngine/g' ../setup.py
    sed -i 's/QAFactor/QDFactor/g' ../setup.py
    sed -i 's/QAFetch/QDFetch/g' ../setup.py
    sed -i 's/QAIndicator/QDIndicator/g' ../setup.py
    sed -i 's/QAMarket/QDMarket/g' ../setup.py
    sed -i 's/QAPubSub/QDPubSub/g' ../setup.py
    sed -i 's/QARSBridge/QDRSBridge/g' ../setup.py
    sed -i 's/QASchedule/QDSchedule/g' ../setup.py
    sed -i 's/QASetting/QDSetting/g' ../setup.py
    sed -i 's/QAStrategy/QDStrategy/g' ../setup.py
    sed -i 's/QASU/QDSU/g' ../setup.py
    sed -i 's/QAUtil/QDUtil/g' ../setup.py
    sed -i 's/QAWebServer/QDWebServer/g' ../setup.py
    echo "✓ setup.py 更新完成"
fi

echo ""
echo "=== 重命名完成 ==="
echo "请检查更改并提交: git status"
echo ""
echo "重命名的目录:"
echo "  QAAnalysis → QDAnalysis"
echo "  QACmd → QDCmd"
echo "  QAData → QDData"
echo "  QADataBridge → QDDataBridge"
echo "  QAEngine → QDEngine"
echo "  QAFactor → QDFactor"
echo "  QAFetch → QDFetch"
echo "  QAIndicator → QDIndicator"
echo "  QAMarket → QDMarket"
echo "  QAPubSub → QDPubSub"
echo "  QARSBridge → QDRSBridge"
echo "  QASchedule → QDSchedule"
echo "  QASetting → QDSetting"
echo "  QAStrategy → QDStrategy"
echo "  QASU → QDSU"
echo "  QAUtil → QDUtil"
echo "  QAWebServer → QDWebServer"
echo "  QIFI → QIFI (保持不变)"
