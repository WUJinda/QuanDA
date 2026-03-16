@echo off
REM QuanDA 模块重命名脚本: QA 前缀 -^> QD 前缀
REM 作者: Claude AI
REM 日期: 2025-03-16

setlocal enabledelayedexpansion

cd /d "%~dp0quanda"

echo === 阶段1: 重命名目录 ===

echo 重命名 QAAnalysis -^> QDAnalysis
git mv QAAnalysis QDAnalysis

echo 重命名 QACmd -^> QDCmd
git mv QACmd QDCmd

echo 重命名 QAData -^> QDData
git mv QAData QDData

echo 重命名 QADataBridge -^> QDDataBridge
git mv QADataBridge QDDataBridge

echo 重命名 QAEngine -^> QDEngine
git mv QAEngine QDEngine

echo 重命名 QAFactor -^> QDFactor
git mv QAFactor QDFactor

echo 重命名 QAFetch -^> QDFetch
git mv QAFetch QDFetch

echo 重命名 QAIndicator -^> QDIndicator
git mv QAIndicator QDIndicator

echo 重命名 QAMarket -^> QDMarket
git mv QAMarket QDMarket

echo 重命名 QAPubSub -^> QDPubSub
git mv QAPubSub QDPubSub

echo 重命名 QARSBridge -^> QDRSBridge
git mv QARSBridge QDRSBridge

echo 重命名 QASchedule -^> QDSchedule
git mv QASchedule QDSchedule

echo 重命名 QASetting -^> QDSetting
git mv QASetting QDSetting

echo 重命名 QAStrategy -^> QDStrategy
git mv QAStrategy QDStrategy

echo 重命名 QASU -^> QDSU
git mv QASU QDSU

echo 重命名 QAUtil -^> QDUtil
git mv QAUtil QDUtil

echo 重命名 QAWebServer -^> QDWebServer
git mv QAWebServer QDWebServer

echo ✓ 目录重命名完成
echo.
echo === 阶段2: 更新所有 Python 文件中的导入语句 ===

REM 使用 Python 进行文本替换（Windows 下更可靠）
python -c "
import os
import re

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换导入语句
        content = re.sub(r'from quanda\.QA([A-Z])', r'from quanda.QD\1', content)
        content = re.sub(r'import quanda\.QA([A-Z])', r'import quanda.QD\1', content)
        content = re.sub(r'from \.QA([A-Z])', r'from .QD\1', content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

# 遍历所有 .py 文件
count = 0
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            if replace_in_file(filepath):
                count += 1

print(f'✓ 更新了 {count} 个 Python 文件')
"

echo.
echo === 阶段3: 更新配置文件 ===

if exist "..\setup.py" (
    python -c "
import re

with open('..\\setup.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有模块名
replacements = [
    ('QAAnalysis', 'QDAnalysis'),
    ('QACmd', 'QDCmd'),
    ('QAData', 'QDData'),
    ('QADataBridge', 'QDDataBridge'),
    ('QAEngine', 'QDEngine'),
    ('QAFactor', 'QDFactor'),
    ('QAFetch', 'QDFetch'),
    ('QAIndicator', 'QDIndicator'),
    ('QAMarket', 'QDMarket'),
    ('QAPubSub', 'QDPubSub'),
    ('QARSBridge', 'QDRSBridge'),
    ('QASchedule', 'QDSchedule'),
    ('QASetting', 'QDSetting'),
    ('QAStrategy', 'QDStrategy'),
    ('QASU', 'QDSU'),
    ('QAUtil', 'QDUtil'),
    ('QAWebServer', 'QDWebServer'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('..\\setup.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ setup.py 更新完成')
"
)

echo.
echo === 重命名完成 ===
echo 请检查更改并提交: git status
echo.
echo 重命名的目录:
echo   QAAnalysis -^> QDAnalysis
echo   QACmd -^> QDCmd
echo   QAData -^> QDData
echo   QADataBridge -^> QDDataBridge
echo   QAEngine -^> QDEngine
echo   QAFactor -^> QDFactor
echo   QAFetch -^> QDFetch
echo   QAIndicator -^> QDIndicator
echo   QAMarket -^> QDMarket
echo   QAPubSub -^> QDPubSub
echo   QARSBridge -^> QDRSBridge
echo   QASchedule -^> QDSchedule
echo   QASetting -^> QDSetting
echo   QAStrategy -^> QDStrategy
echo   QASU -^> QDSU
echo   QAUtil -^> QDUtil
echo   QAWebServer -^> QDWebServer
echo   QIFI -^> QIFI (保持不变)

endlocal
