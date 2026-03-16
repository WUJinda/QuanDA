# coding=utf-8
#
# The MIT License (MIT)
#
"""
这里主要是一些关于文本的代码

文本分词
模糊查询
正则匹配
"""

import jieba
import re
import fuzzyfinder

# 🛠TODO: stock_list中有股票的中文/stock_block中有版块的中文 需要将他们做一些模糊查询



def split_word(input_text,cutall=False):
    """
    使用jieba分词 将输入的语句分词
    """

    return jieba.cut(input_text,cut_all=cutall)
