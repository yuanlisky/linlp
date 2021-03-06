# -*- coding: utf-8 -*-
from linlp.algorithm.Viterbi import viterbiRecognitionPerson
from linlp.algorithm.viterbiMat.prob_trans_person import prob_trans as trans_p
from linlp.algorithm.viterbiMat.prob_emit_person import prob_emit as emit_p


def personviterbiSimply(obs, DT, obsDT, debug):
    if debug:
        x = obs
    switch = {'nr': 1, 'nnt': 2}
    length = len(obs)
    for no in range(length):
        case = switch.get(obs[no][1], 0)
        if not DT.tree.get(obs[no][0]):
            if case == 1:  # 词语不在人名字典且词性为nr时
                # 有些双名实际上可以构成更长的三名
                if len(obs[no][0]) == 2 and obsDT.tree[obs[no][0]]['total'] <= 1000:
                    DT.tree[obs[no][0]] = {'X': 1, 'G': 1}
                else:
                    DT.tree[obs[no][0]] = {'A': 22202445}
            elif case == 2:  # 词语不在人名字典且词性为nnt时
                # 姓 + 职位
                DT.tree[obs[no][0]] = {'G': 1, 'K': 1}
            else:
                DT.tree[obs[no][0]] = {'A': 22202445}
        # elif obs[no][0] == '始##始':
        #     DT.tree[obs[no][0]] = {'A': 22202445}
    path = viterbiRecognitionPerson(obs, trans_p, emit_p, DT)
    if debug:
        s = ''
        t = '['
        l = len(x)
        for i in range(l):
            word = x[i]
            s += '[' + word[0] + ' '
            t += word[0]
            for k, v in DT.tree[obs[i][0]].items():
                if k == 'total':
                    continue
                s += k + ':' + str(v) + ' '
            s += ']'
            t += '/' + path[i] + ', '
        t += ']'
        print('人名角色观察: %s' % s)
        print('人名角色标注: %s' % t)
    return path
