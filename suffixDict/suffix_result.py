#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@time: 2017/2/24 17:09
@author: yl
"""
import re
# 利用地名词典BJplaceDone.txt，以及总结的后缀词典classify.txt对BJplace.txt文件中的词条进行切分。设BJplace.txt中有词条A，实现过程为：
# ① 搜索A在地名词典BJplaceDone.txt中的最大正向匹配a；
# ② 倒序搜索a后7个字符是否有字符串s包含在后缀词典classify.txt中，搜索范围为随机确定，目前暂定为7；
# ③ 将a至s及中间的字符串拼接，组成新词条。
# 最后得到地址信息词条切分文件classify_result.txt


class buildDict(object):
    def __init__(self):
        pass

    # <editor-fold desc="载入文件">
    # 将词典文件载入，保存成Python的字典类型
    def loadfile(self, f):
        '''
        :param f: 载入字典文件
        :return: 将字典文件按行保存到Python字典中
        '''
        dt = {}  # 将BJplaceDone中的词存入dt中
        with open(f, encoding='utf-8') as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                line = re.sub("([^\u4E00-\u9FD5])", '', line)
                dt[line] = 1
        return dt
    # </editor-fold>

    # <editor-fold desc="最长词语的长度">
    def gen_longest(self, dt):
        l = 1
        for s in dt.keys():
            s = str(s)
            if len(s) > l:
                l = len(s)
        return l
    # </editor-fold>

    # <editor-fold desc="获取前缀词典">
    def gen_pfdict(self, f):
        '''
        :param f: 载入字典文件
        :return: 输出字典的前缀词典，字典中的词value为1，前缀词value为0
        '''
        dt = self.loadfile(f)
        ldt = {}  # 前缀词典
        for x in dt.keys():
            ldt[x] = 1  # 在字典dt中存在的词，在ldt中的value为1
            for y in range(1, len(x)):
                if not x[:y] in dt:
                    ldt[x[:y]] = 0  # 字典dt中的词的前缀词语，value为0
        return ldt
    # </editor-fold>

    # <editor-fold desc="获取结果字典">
    def gen_dict(self, sourcefile, dictfile, suffixfile, resultfile, linenum=None, lensuffix=7):
        '''
        :param sourcefile: 样本信息文件
        :param dictfile: HanLP对样本文件进行分词并经过进一步处理的文件
        :param suffixfile: 后缀字典文件
        :param resultfile: 结果输出文件
        :param linenum: 处理样本信息文件前linenum行
        :param lensuffix: 正向最大匹配词语向后搜索后缀的位数
        :return: 生成结果输出文件
        '''
        res = {}  # 正向最大匹配dt字典中的词
        suf = {}  # res中的词与后缀信息合并
        ldt = self.gen_pfdict(dictfile)  # 通过地名词典文件，建立前缀词典ldt
        suffix = self.loadfile(suffixfile)  # 后缀词典
        suffixlength = self.gen_longest(suffix)  # 后缀词典最长词组
        if suffixlength > lensuffix:
            raise ValueError('number of lensuffix must longer than the longest word of suffix.')
        wr = open(resultfile, 'a+', encoding='utf-8')  # 结果写入classify_result.txt文件
        with open(sourcefile, encoding='utf-8') as f:  # 读取BJplace.txt文件
            for lineno, line in enumerate(f, 1):  # 逐行读取BJplace.txt文件信息
                print('Processing line: ', lineno)
                line = line.strip()  # 词条样本
                x = 0  # line的指针
                while x < len(line):
                    temp = None  # 重置临时字符变量
                    if line[x] in ldt.keys():  # 如果第x个字在前缀词典中(不在字典中则直接令x+=1，跳入下一循环)
                        for i in range(len(line)-x):  # line从第x字开始，还剩i个字符就做i次循环
                            if line[x:x+i+1] in ldt.keys():   # 如果从第x个字到第i个字的词语在前缀词典中
                                if ldt.get(line[x:x+i+1]):  # 判断该词语在前缀词典中的value是不是1，是1就表示在dt词典中
                                    temp = line[x:x+i+1]  # 将匹配dt的词语赋给临时变量temp
                                    # 如果此时x到i的词语已经到了句末且存在于dt中，直接保存该词语到正向最大匹配dt字典，并将x指针指向句末
                                    if len(line) == x+i+1:
                                        res[temp] = 1
                                        x = x+i+1
                            else:  # 如果从第x个字到第i个字的词语不在前缀词典中，那么就要找从x到i之前的匹配dt的，即需要找temp
                                if temp:  # 如果temp存在，就表示从x到i之前的匹配dt的词语存在，且为temp
                                    res[temp] = 1  # 保存最大正向匹配结果
                                    for j in range(lensuffix, 0, -1):  # 从远到近搜索最大正向匹配词语之后的j个字符
                                        s = line[x+i:x+i+j]  # temp词语后面的j个字符
                                        if len(s) != j:  # 如果s的长度不等于j的长度，表示temp到句末的长度不足j，跳出此次循环，避免重复写入
                                            continue
                                        for k in range(suffixlength):
                                            r = line[x+i+j-1-k:x+i+j]  # r 为 s 最后的k+1个字符，k 依次为 0、1、2
                                            if r in suffix.keys():  # 如果r中包含后缀词语
                                                # 将 最大正向匹配的词语temp和 末尾为后缀词语的字符串s，组成新词条，存入suf，并跳出k循环
                                                suf[temp+s] = 1
                                                wr.write(temp+s+', ') # 写入wr文件
                                                break
                                        # 如果k不等于2，表示找到此次最远的后缀词语，跳出j循环（从远到近搜索最大正向匹配词语之后的j个字符）
                                        if suffixlength-1 != k:
                                            break
                                    x = x + len(temp)-1  # 如果temp存在，x先要指向temp的最后一个字符位置，后面x+=1才指向temp之后的一位
                                # 跳出i循环(第i个字符不在前缀词典中，那么加上i后面的字符也不可能在前缀词典中，所以直接跳出i循环，指向下位置字符串
                                break
                    x += 1  # 对应循环中第一个if不成立时的处理
                wr.write('\n')  # 换行
                if lineno == linenum:  # 处理到指定行数，则跳出循环，停止处理
                    break
        wr.close()
        print('Done')
    # </editor-fold>


if __name__ == '__main__':
    DT = buildDict()
    DT.gen_dict(sourcefile='./dictionary/BJplace.txt', dictfile='./result/BJplaceDone.txt',
                suffixfile='./dictionary/classify.txt', resultfile='classify_result1.txt',
                linenum=1000)