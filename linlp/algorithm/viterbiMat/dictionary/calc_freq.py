#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: yl
"""
import numpy as np
import sys
import os
__all__ = ['calc_MAT', ]


def calc_MAT(dictfile, trfile):
    MIN_FLOAT = -3.14e+100
    POS_freq = {}  # {'词性': 频数}
    dict_line = {}  # {'词':{'词性1':频数, '词性2':频数}}

    with open(dictfile, 'r', encoding='utf-8') as f:
        for x in f.readlines():
            x = x.strip()
            line = x.split(' ')
            word = line[0]
            POS = line[1::2]
            freq = list(map(int, line[2::2]))
            dict_line[word] = {}
            for y in range(len(POS)):
                temp = POS_freq.get(POS[y], 0)
                POS_freq.update({POS[y]: temp + freq[y]})
                dict_line[word].update({POS[y]: freq[y]})

    with open(trfile, 'r', encoding='utf-8') as f:
        trans_list = []
        POS_list = f.readline().strip().split(',')[1::]
        for POSlength in range(len(POS_list)):
            trans_list.append(list(map(int, f.readline().strip().split(',')[1::])))
    trans_MAT = np.array(trans_list)
    max_freq = trans_MAT.sum()
    # POS_freq['Z'] = trans_MAT.sum(1)[POS_list.index('Z')]

    # 查看字典词性频数与字典对应转移矩阵的频数误差
    a = POS_freq
    b = POS_list
    c = list(trans_MAT.sum(1))
    print('POS| dict_freq| tr_freq')
    for l in range(len(b)):
        if c[l] == 0:
            c[l] = trans_MAT.sum(0)[l]
        print('%r| %r| %r' % (b[l], a[b[l]], c[l]))

    start_p = dict()
    for p in POS_list:
        start_p[p] = MIN_FLOAT
    begin = list(dict_line['始##始'].keys())[0]
    start_p[begin] = np.log(1)

    # 根据tr.txt文件计算转移矩阵
    trans_p = dict()
    for x in range(len(POS_list)):
        trans_p[POS_list[x]] = {}
        for y in range(len(POS_list)):
            if trans_MAT[x][y] != 0:
                trans_p[POS_list[x]].update({POS_list[y]: np.log(trans_MAT[x][y]/max_freq)})
            else:
                trans_p[POS_list[x]].update({POS_list[y]: MIN_FLOAT})

    # 发射概率，观测态(字词)在隐形态(词性)下出现的概率，即某隐态下，某词出现的概率
    # P(Observed[i]|Status[j]) = P(Status[j]|Observed[i])*P(Observed[i])/P(Status[j])
    # 根据字典文件计算发射矩阵
    emit_p = dict()
    for x in POS_list:
        emit_p[x] = {}
    for word in dict_line.keys():
        for POS, POSfreq in dict_line[word].items():
            if POS not in emit_p.keys():
                continue
            emit_p[POS].update({word: np.log(POSfreq/POS_freq[POS])})

    return start_p, trans_p, emit_p


def output(start_p, trans_p, emit_p, name):
    __console__ = sys.stdout
    with open(os.path.abspath('../prob_start_%s.py' % name), 'w', encoding='utf8') as start:
        sys.stdout = start
        # print('prob_start = ', start_p)
        print('prob_start = {')
        for k, v in start_p.items():
            print("%r: %r," % (k, v))
        print('}')
    with open(os.path.abspath('../prob_trans_%s.py' % name), 'w', encoding='utf8') as trans:
        sys.stdout = trans
        # print('prob_trans = ', trans_p)
        print('prob_trans = {')
        for x in trans_p.keys():
            print("%r: {" % x)
            for k, v in trans_p[x].items():
                print("%r: %r," % (k, v))
            print('},')
        print('}')
    with open(os.path.abspath('../prob_emit_%s.py' % name), 'w', encoding='utf8') as emit:
        sys.stdout = emit
        # print('prob_emit = ', emit_p)
        print('prob_emit = {')
        for x in emit_p.keys():
            print("%r: {" % x)
            for k, v in emit_p[x].items():
                print("%r: %r," % (k, v))
            print('},')
        print('}')
    sys.stdout = __console__


if __name__ == '__main__':
    s, t, e = calc_MAT(r'.\person\nr.txt',
                       r'.\person\nr.tr.txt')
    output(s, t, e, 'person')
