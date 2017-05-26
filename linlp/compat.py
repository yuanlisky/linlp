# -*- coding: utf-8 -*-
"""
需要用到的变量、表达式：
    正则表达式
    AC自动机
    字典树类
"""
import re
from linlp.const import *
from linlp.algorithm import AhoCorasick


class DictTree(object):
    """
    根据词典文件，建立字典树
    结构：
        DT.tree = {word1:{'total': num, 词性1: num1, 词性2: num2, ...},
                   word2:{'total': num, 词性1: num1, 词性2: num2, ...}}
    """
    def __init__(self):
        self.tree = dict()

    def add(self, line):
        tree = self.tree
        tree[line[0]] = dict()
        l = len(line)
        total = 0
        for v in range(1, l, 2):
            tree[line[0]][line[v]] = int(line[v+1])
            total += int(line[v+1])
        tree[line[0]]['total'] = total


def AC_make(AC_list):
    """
    建立AC自动机
    参数：
        - AC_list: 目标模式串，list类型，元素为字符串
    返回：
        ah: AC自动机
    """
    ah = AhoCorasick.Ahocorasick()
    for x in AC_list:
        ah.addWord(x)
    ah.make()
    return ah

person = AC_make(AC_person)  # 人名识别的AC自动机
place = AC_make(AC_place)  # 地名识别的AC自动机
organization = AC_make(AC_organization)  # 机构名识别的AC自动机

# region 正则表达式
re_eng = re.compile('[a-zA-Z0-9]', re.U)  # 匹配单个字母或数字
re_en = re.compile('[a-zA-Z]+', re.U)  # 匹配字母
re_en_1 = re.compile('[a-zA-Z]', re.U)  # 匹配单个字母
re_num = re.compile('\+?-?[0-9]*$', re.U)  # 匹配整数
re_num_1 = re.compile('[0-9]', re.U)  # 匹配单个数字
re_num_f = re.compile('\+?-?[0-9]+\.?[0-9]*$', re.U)  # 匹配浮点数
re_num_cn = re.compile('[一二三四五六七八九十百千万亿兆]+', re.U)  # 匹配汉字简写数字
re_skip_default = re.compile("(\r\n|\s+)", re.U)  # 匹配换行和空格
re_han_cut_all = re.compile("([\u4E00-\u9FD5]+)", re.U)  # 匹配汉字，可用来粗分
re_skip_cut_all = re.compile("[^a-zA-Z0-9+#\n]", re.U)  # 不匹配字母数字，井号，换行符
# endregion

if __name__ == '__main__':
    s = '31# '
    s = '欢迎来到3-31.#python java\r\n'
    print('re_eng:', re_eng.split(s))
    print('re_han_cut_all_匹配汉字:', re_han_cut_all.split(s))
    print('re_skip_default_匹配换行和空格:', re_skip_default.split(s))
    print('re_skip_cut_all_不匹配字母数字，井号，换行符:', re_skip_cut_all.split(s))
    print(__file__)
