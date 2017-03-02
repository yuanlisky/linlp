#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@time: 2017/2/16 16:14
@author: yl
"""
from jpype import *
import re
# 使用Python调用自然语言处理包HanLP，对词条进行初步分词。


class HanLPseg(object):
    def __init__(self, javapath, javafile):
        self.javapath = javapath
        self.javafile = javafile

    def seg(self, sourcefile, resultfile, model='N', linenum=None):
        '''
        :param sourcefile: 源文件，地理信息样本
        :param resultfile: 结果文件，使用HanLP分词器分词后结果
        :param model: 分词模式，'P': 开启地址识别；'O': 开启机构识别；'A': 两种识别都开启；默认都不开启
        :param linenum: 读取源文件前linenum行地理信息
        :return: 无返回,生成分词结果文件resultfile
        '''
        startJVM(getDefaultJVMPath(), ("-Djava.class.path=%s;%s" % (self.javafile, self.javapath)), "-Xms1g", "-Xmx1g")
        HanLP = JClass('com.hankcs.hanlp.HanLP')
        x = HanLP.newSegment()
        if model == 'P':
            x.enablePlaceRecognize(True)  # 开启地址识别
        elif model == 'O':
            x.enableOrganizationRecognize(True)  # 开启机构识别
        elif model == 'A':
            x.enablePlaceRecognize(True)
            x.enableOrganizationRecognize(True)
        f = open(sourcefile, 'rb')
        wr = open(resultfile, 'a+', encoding='utf8')
        word = {} # 将分词结果存入字典
        for lineno, line in enumerate(f, 1):  # 逐行读取文件f, 使用enumerate比较省内存
            line = line.strip().decode('utf-8')
            w = line.split(' ')[0]
            s = re.sub("([^a-zA-Z0-9+#\n\u4E00-\u9FD5])", '', w)
            for res in x.seg2sentence(s):
                # x.seg2sentence(s) 为分词结果, 形式：[[北京市/ns, 房山/ns, 区/n, 窦店镇/ns, 于庄/ns, 锦绣路/ns, 18/m, 号/q]]
                for z in res:
                    r = str(z) # 转变为字符串格式
                    # if model == 'P':
                    #     if not ('/ns' in r or '/nz' in r or '/nsf' in r):
                    #         r = re.sub("([^\u4E00-\u9FD5])", '', r) # 保留 /ns, /nsf, /nz 的词性注释
                    # elif model == 'O':
                    #     if not ('/nt' in r or '/nz' in r):
                    #         r = re.sub("([^\u4E00-\u9FD5])", '', r)
                    # elif model == 'A':
                    #     if not ('/ns' in r or '/nz' in r or '/nsf' in r or '/nt' in r):
                    #         r = re.sub("([^\u4E00-\u9FD5])", '', r)
                    if r not in word and r != '':  # '判断r是否在word中且不为""' ，避免重复
                        word[r] = 1
                        wr.write(r + '\n')
            print('Processing line: ', lineno)
            if lineno == linenum:
                break
        f.close()
        wr.close()
        print('Done！')
        shutdownJVM()


if __name__ == '__main__':
    s = HanLPseg(javapath='C:\hanlp', javafile='C:\hanlp\hanlp-1.3.2.jar')
    s.seg('./dictionary/BJplace.txt', './B1.txt', model='P', linenum=100)
