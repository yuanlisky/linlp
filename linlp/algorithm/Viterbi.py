# -*- coding: utf-8 -*-
"""
Viterbi算法
"""
from linlp.const import MIN_FLOAT
from linlp.algorithm.viterbiMat.prob_start_jieba import start_p_jieba
from linlp.algorithm.viterbiMat.prob_trans_jieba import trans_p_jieba
from linlp.algorithm.viterbiMat.prob_emit_jieba import emit_p_jieba

PrevStatus = {
    'B': 'ES',
    'M': 'MB',
    'S': 'SE',
    'E': 'BM'
}


def viterbi(obs, states):
    V = [{}]
    path = dict()
    for y in states:
        V[0][y] = start_p_jieba[y] + emit_p_jieba[y].get(obs[0], MIN_FLOAT)
        path[y] = [y]
    for t in range(1, len(obs)):
        V.append({})
        newpath = dict()
        for y in states:
            em_p = emit_p_jieba[y].get(obs[t], MIN_FLOAT)
            (prob, state) = max([(V[t-1][y0] + trans_p_jieba[y0].get(y, MIN_FLOAT) + em_p, y0) for y0 in PrevStatus[y]])
            V[t][y] = prob
            newpath[y] = path[state] + [y]
        path = newpath
    (prob, state) = max((V[len(obs) - 1][y], y) for y in 'ES')
    return path[state]


def viterbiRecognitionPerson(obs, trans_p, emit_p, DT):
    tagList = list()
    pre = 'A'
    for t in range(len(obs)):
        (prob, state) = max([(trans_p[pre][y]+emit_p[y].get(obs[t][0], -100), y)
                             for y in DT.tree.get(obs[t][0]).keys() if y != 'total'])
        pre = state
        tagList.append(pre)
    return tagList


def viterbiRecognitionSimply(obs, trans_p, emit_p, DT):
    V = [{}, {}]
    tagList = list()
    for y in DT.tree[obs[0][0]].keys():
        if y == 'total':
            continue
        tagList.append(y)
    for y in DT.tree[obs[1][0]].keys():
        if y == 'total':
            continue
        V[0][y] = trans_p[tagList[0]][y] + emit_p[y].get(obs[1][0], -100)
    for t in range(2, len(obs)):
        index_i = 1 - t & 1
        V[index_i] = dict()
        cost = MIN_FLOAT
        p = 'Z'
        for y in DT.tree.get(obs[t][0]).keys():  # 词性
            if y == 'total':
                continue
            em_p = emit_p[y].get(obs[t][0], -100)  # y状态下，观测到第t个字的概率
            (prob, state) = max([(V[1-index_i][y0]+trans_p[y0].get(y, -100)+em_p, y0) for y0 in V[1-index_i].keys()])
            V[index_i][y] = prob
            if cost < prob:
                cost = prob
                p = state
        tagList.append(p)
    tagList.append(tagList[0])
    return tagList


def viterbiSimply(obs, DT):
    path = ['begin']
    for no, v in enumerate(obs):
        freq = 0
        state = 'x'
        if DT.tree.get(v):
            for POS, f in DT.tree.get(v).items():
                if POS == 'total':
                    continue
                if freq < f:
                    freq = f
                    state = POS
        else:
            state = 'x'
        path.append(state)
    return path[1:]


if __name__ == '__main__':
    pass
