# coding:utf-8
"""
上传配置文件
用于配置图片、文件等上传路径
"""

import os

# 默认上传根目录（相对于项目根目录）
DEFAULT_UPLOAD_ROOT = 'uploads'

# 策略参照库图片上传目录
STRATEGY_REFERENCE_UPLOAD_DIR = 'strategy-reference'

# 获取完整的上传路径
def get_upload_path(sub_dir=''):
    """
    获取上传文件的完整路径
    
    Args:
        sub_dir: 子目录名称
    
    Returns:
        完整的上传路径
    """
    # 可以从环境变量读取自定义路径
    upload_root = os.environ.get('QUANDA_UPLOAD_ROOT', DEFAULT_UPLOAD_ROOT)
    
    if sub_dir:
        return os.path.join(upload_root, sub_dir)
    return upload_root


# 获取策略参照库上传路径
def get_strategy_reference_upload_path():
    """获取策略参照库图片上传路径"""
    return get_upload_path(STRATEGY_REFERENCE_UPLOAD_DIR)


# 获取文件访问URL
def get_file_url(relative_path):
    """
    获取文件的访问URL
    
    Args:
        relative_path: 相对于上传根目录的路径
    
    Returns:
        文件访问URL
    """
    # 确保路径以 / 开头
    if not relative_path.startswith('/'):
        relative_path = '/' + relative_path
    
    return relative_path
