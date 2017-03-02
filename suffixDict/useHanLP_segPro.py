#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@time: 2017/2/20 9:18
@author: yl
"""
import re
# 处理HanLP的分词结果：① 过滤1个字的词语；② 选择词性为’ns’，’nsf’，’nz’的词语。


class SegPro(object):
    def __init__(self):
        pass

    def process(self, sourcefile, resultfile, tag, filterlength=1):
        '''
        :param sourcefile: HanLP分词结果文件
        :param resultfile: 对HanLP分词结果进行处理，输出txt文件
        :param tag: 过滤词性不为tag的词语,tag为列表
        :param filterlength：过滤长度为filterlength的词语
        :return:
        '''
        f = open(sourcefile,'rb')
        wr = open(resultfile, 'a+', encoding='utf8')
        t = tag
        for lineno, line in enumerate(f, 1):
            line = line.strip().decode('utf-8')
            s = line.split(' ')[0]
            r = re.sub("([^\u4E00-\u9FD5])", '', s)
            if len(r) == filterlength:
                continue
            # if ('/nt' in s or '/nz' in s or '/ns' in s or '/nsf' in s):
            if self.tagging_filter(s, t):
                wr.write(s + '\n')
                print('Processing line: ', lineno)
        f.close()
        wr.close()
        print('Done!')

    def tagging_filter(self, s, tag):
        for x in tag:
            if x in s:
                return 1
        return 0


if __name__ == '__main__':
    tag = ['/nt', '/nz', '/ns', '/nsf']
    segpro = SegPro()
    segpro.process('./result/BJplacePro.txt', './BJ1.txt', tag, filterlength=1)