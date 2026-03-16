"""
因子研究的基础


- 数据清洗

- 因子研究的env_panel

- 因子标准化数据的存储和读取

- 因子


"""

from quanda.QDFactor.feature import QASingleFactor_DailyBase
from quanda.QDFactor.featurepool import MA10
from quanda.QDFactor.featureView import QAFeatureView
try:
    from quanda.QDFactor.featureAnalysis import QAFeatureAnalysis
except ImportError:
    QAFeatureAnalysis = None
try:
    from quanda.QDFactor.featurebacktest import QAFeatureBacktest
except ImportError:
    QAFeatureBacktest = None