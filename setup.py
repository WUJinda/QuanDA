# coding=utf-8
#
# The MIT License (MIT)
#
import codecs
import io
import os
import re
import sys
import webbrowser
import platform
import configparser
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # deprecated in 3.12, fallback for older
"""
"""

# 检查Python版本 - 支持3.9-3.13
if sys.version_info < (3, 9) or sys.version_info >= (4, 0):
    print('=' * 60)
    print('错误: QuanDA 2.1+ 需要 Python 3.9-3.13')
    print(f'当前版本: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
    print('=' * 60)
    print('\n推荐使用:')
    print('  - Python 3.9+ (与QARS2 Rust核心兼容)')
    print('  - Python 3.11-3.13 (最佳性能)')
    print('\n升级方法:')
    print('  Ubuntu/Debian: sudo apt install python3.11')
    print('  macOS: brew install python@3.11')
    print('  Windows: https://www.python.org/downloads/')
    print('=' * 60)
    sys.exit(1)

with io.open('quanda/__init__.py', 'rt', encoding='utf8') as f:
    context = f.read()
    VERSION = re.search(r'__version__ = \'(.*?)\'', context).group(1)
    AUTHOR = re.search(r'__author__ = \'(.*?)\'', context).group(1)


# 注释掉自动打开浏览器的代码，避免安装时弹出页面
# try:
#     if sys.platform in ['win32', 'darwin']:
#         print(webbrowser.open(
#             'https://github.com/WUJinda/QuanDA/releases'))
#         print('finish install')
# except:
#     pass


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()


NAME = "quanda"
"""

"""
PACKAGES = [
    "quanda",
    "quanda.QAFetch",
    "quanda.QACmd",
    "quanda.QASetting",
    "quanda.QAFactor",
    "quanda.QAEngine",
    "quanda.QAData",
    "quanda.QAAnalysis",
    "quanda.QAPubSub",
    "quanda.QASU",
    "quanda.QAUtil",
    "quanda.QAIndicator",
    "quanda.QAStrategy",
    "quanda.QAMarket",
    "quanda.QIFI",
    "quanda.QAWebServer",
    "quanda.QASchedule",      # v2.1.0新增: 任务调度框架
    "quanda.QARSBridge",      # v2.1.0新增: Rust桥接层 (100x加速)
    "quanda.QADataBridge",    # v2.1.0新增: 跨语言零拷贝通信 (5-10x加速)
]
"""

"""

DESCRIPTION = "QuanDA: Quantitative Financial Strategy Framework"


# try:
#     import pypandoc
#     LONG_DESCRIPTION = pypandoc.convert_file('README.md', 'rst')
# except Exception:
# with open("README_ENG.md", "r", encoding='utf-8') as fh:
#     LONG_DESCRIPTION = fh.read()
LONG_DESCRIPTION = 'QuanDA Financial Framework'

"""

"""

KEYWORDS = ["quanda", "quant", "finance", "Backtest", 'Framework']
"""

"""

AUTHOR_EMAIL = "contact@quanda.io"

URL = "https://github.com/WUJinda/QuanDA"


LICENSE = "MIT"

with open('requirements.txt', encoding='utf-8') as reqs_file:
    INSTALL_REQUIRES = [
        line.strip() for line in reqs_file
        if line.strip() and not line.strip().startswith('#')
    ]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
    install_requires=INSTALL_REQUIRES,
    # Python版本要求 - 支持3.9-3.13
    python_requires='>=3.9,<3.14',
    # 可选依赖: Rust高性能组件
    extras_require={
        'rust': [
            'qars3>=0.0.45',  # QARS2 Rust核心 (PyO3绑定)
            'qadataswap>=0.1.0',  # 跨语言零拷贝通信
        ],
        'performance': [
            'polars>=0.20.0',  # 高性能数据处理，支持Python 3.13
            'orjson>=3.10.0',  # 快速JSON序列化
            'msgpack>=1.1.0',  # MessagePack序列化
        ],
        'full': [
            'qars3>=0.0.45',
            'qadataswap>=0.1.0',
            'polars>=0.20.0',
            'orjson>=3.10.0',
            'msgpack>=1.1.0',
            'jupyter>=1.0.0',
            'jupyterlab>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'quanda=quanda.QACmd:QA_cmd',
            'quandaq=quanda.QAFetch.QATdx_adv:bat',
            'qarun=quanda.QACmd.runner:run',
            'qawebserver=quanda.QAWebServer.server:main',
        ]
    },
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False  # 改为False，因为包含Rust扩展
)
