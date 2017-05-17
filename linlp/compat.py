# -*- coding: utf-8 -*-
import re
from linlp.const import *
from linlp.algorithm import AhoCorasick


re_eng = re.compile('[a-zA-Z0-9]', re.U)

re_en = re.compile('[a-zA-Z]+', re.U)  # 用 search 匹配任意位置的字母
re_en_1 = re.compile('[a-zA-Z]', re.U)
re_num = re.compile('[0-9]+', re.U)  # fullmatch 只包含数字
re_num_1 = re.compile('[0-9]', re.U)
re_num_f = re.compile('[0-9]+\.?[0-9]*', re.U)  # fullmatch 只包含数字
re_num_cn = re.compile('[一二三四五六七八九十百千万亿兆]+', re.U)

# \r\n 回车符,ASCII 模式下换行符会在读写时自动换为 \r\n，匹配换行和空格
re_skip_default = re.compile("(\r\n|\s+)", re.U)

re_han_cut_all = re.compile("([\u4E00-\u9FD5]+)", re.U)  # 匹配汉字  可用来粗分

re_skip_cut_all = re.compile("[^a-zA-Z0-9+#\n]", re.U)  # 不匹配字母数字，井号，换行符


def AC_make(AC_list):
    ah = AhoCorasick.Ahocorasick()
    for x in AC_list:
        ah.addWord(x)
    ah.make()
    return ah
person = AC_make(AC_person)
place = AC_make(AC_place)
organization = AC_make(AC_organization)


class DictTree(object):
    """
    字典树
    {word:{total: num, 词性1: num, 词性2: num, ...}}
    """
    def __init__(self):
        self.tree = {}

    def add(self, line):
        tree = self.tree
        tree[line[0]] = {}
        l = len(line)
        total = 0
        for v in range(1, l, 2):
            tree[line[0]][line[v]] = int(line[v+1])
            total += int(line[v+1])
        tree[line[0]]['total'] = total

if __name__ == '__main__':
    s = '31# '
    s = '欢迎来到3-31.#python java\r\n'
    print('re_eng:', re_eng.split(s))
    print('re_han_cut_all_匹配汉字:', re_han_cut_all.split(s))
    print('re_skip_default_匹配换行和空格:', re_skip_default.split(s))
    print('re_skip_cut_all_不匹配字母数字，井号，换行符:', re_skip_cut_all.split(s))
    print(__file__)
