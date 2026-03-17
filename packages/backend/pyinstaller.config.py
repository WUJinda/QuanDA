# -*- mode: python ; coding: utf-8 -*-

"""
QuanDA Python 后端 PyInstaller 配置
用于将 Python 后端打包为独立可执行文件
"""

import sys
import os
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = Path(__file__).parent
QUANDA_DIR = BACKEND_DIR / 'quanda'

block_cipher = None

# 收集所有需要的导入
hidden_imports = [
    'quanda',
    'quanda.QDWebServer',
    'quanda.QDWebServer.server',
    'quanda.QDWebServer.basehandles',
    'quanda.QDWebServer.commandhandler',
    'quanda.QDWebServer.handlers',
    'quanda.QDData',
    'quanda.QDEngine',
    'quanda.QDIndicator',
    'quanda.QDMarket',
    'quanda.QDPubSub',
    'quanda.QDSetting',
    'quanda.QDSU',
    'quanda.QDFetch',
    'quanda.QDUtil',
    'quanda.QIFI',
    'tornado',
    'tornado.web',
    'tornado.ioloop',
    'tornado.options',
    'pymongo',
    'clickhouse_driver',
    'redis',
    'pandas',
    'numpy',
]

# 数据分析相关的隐藏导入
hidden_imports.extend([
    'pandas._libs.tslibs.base',
    'pandas._libs.tslibs.dtypes',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.parsing',
    'pandas._libs.tslibs.timestamps',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.period',
    'pandas._libs.hashtable',
    'pandas._libs.lib',
    'pandas._libs.index',
])

# 收集数据文件
datas = [
    (str(QUANDA_DIR / 'config'), 'quanda/config'),
]

# 收集二进制文件
binaries = []

a = Analysis(
    [str(QUANDA_DIR / 'QDWebServer' / 'server.py')],
    pathex=[str(BACKEND_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='quanda-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
