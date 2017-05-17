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
    path = {}
    for y in states:
        V[0][y] = start_p_jieba[y] + emit_p_jieba[y].get(obs[0], MIN_FLOAT)
        path[y] = [y]
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}
        for y in states:
            em_p = emit_p_jieba[y].get(obs[t], MIN_FLOAT)
            (prob, state) = max([(V[t-1][y0] + trans_p_jieba[y0].get(y, MIN_FLOAT) + em_p, y0) for y0 in PrevStatus[y]])
            V[t][y] = prob
            newpath[y] = path[state] + [y]
        path = newpath
    (prob, state) = max((V[len(obs) - 1][y], y) for y in 'ES')
    return path[state]


def viterbiRecognition(obs, start_p, trans_p, emit_p, DT):
    V = [{}]
    path = dict()
    for y in DT.tree[obs[0][0]].keys():
        if y == 'total':
            continue
        V[0][y] = start_p[y] + emit_p[y].get(obs[0][0], -100)
        path[y] = [y]
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}
        for y in DT.tree.get(obs[t][0]).keys():
            if y == 'total':
                continue
            em_p = emit_p[y].get(obs[t][0], -100)  # y状态下，观测到第t个字的概率
            (prob, state) = max([(V[t-1][y0] + trans_p[y0].get(y, -100) + em_p, y0) for y0 in V[t-1].keys()])
            V[t][y] = prob
            newpath[y] = path[state] + [y]
        path = newpath
    end = list()
    for e in DT.tree.get(obs[-1][0]).keys():
        if e == 'total':
            continue
        end.append(e)
    (prob, state) = max((V[len(obs)-1][y], y) for y in end)
    return path[state]


def viterbiSimply(obs, trans_p, DT, default):
    path = ['begin']
    for no, v in enumerate(obs):
        prob = MIN_FLOAT
        freq = 0
        state = default
        state_temp = default
        if DT.tree.get(v):
            for POS, f in DT.tree.get(v).items():
                if POS == 'total':
                    continue
                if prob < trans_p[path[no]][POS]:
                    prob = trans_p[path[no]][POS]
                    state = POS
                if freq < f:
                    freq = f
                    state_temp = POS
                if prob == MIN_FLOAT:
                    state = state_temp
        else:
            state = default
        path.append(state)
    return path[1:]


if __name__ == '__main__':
    # 观测序列
    obs_example = ['walk', 'shop', 'clean']

    # 隐状态
    states_example = ['Rainy', 'Sunny']

    # 初始概率
    start_p_example = {'Rainy': -0.51082562376599072, 'Sunny': -0.916290731874155}
    # start_p_example = {'Rainy': np.log(0.6), 'Sunny': np.log(0.4)}

    # 转移概率
    trans_p_example = {'Rainy': {'Rainy': -0.35667494393873245, 'Sunny': -1.2039728043259361},
                       'Sunny': {'Rainy': -0.916290731874155, 'Sunny': -0.51082562376599072}
                       }
    # trans_p_example = {'Rainy': {'Rainy': np.log(0.7), 'Sunny': np.log(0.3)},
    #                    'Sunny': {'Rainy': np.log(0.4), 'Sunny': np.log(0.6)}
    #                    }

    # 发射概率(观测概率)
    emit_p_example = {'Rainy': {'walk': -2.3025850929940455, 'shop': -0.916290731874155, 'clean': -0.69314718055994529},
                      'Sunny': {'walk': -0.51082562376599072, 'shop': -1.2039728043259361, 'clean': -2.3025850929940455}
                      }
    # emit_p_example = {'Rainy': {'walk': np.log(0.1), 'shop': np.log(0.4), 'clean': np.log(0.5)},
    #                   'Sunny': {'walk': np.log(0.6), 'shop': np.log(0.3), 'clean': np.log(0.1)}
    #                   }

    # print(viterbi(obs_example, states_example, start_p_example, trans_p_example, emit_p_example))
    # ['Sunny', 'Rainy', 'Rainy']
