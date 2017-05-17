# -*- coding: utf-8 -*-
from linlp.algorithm.Viterbi import viterbiRecognition
from linlp.algorithm.viterbiMat.prob_trans_place import prob_trans as trans_p
from linlp.algorithm.viterbiMat.prob_emit_place import prob_emit as emit_p
from linlp.algorithm.viterbiMat.prob_start_place import prob_start as start_p


def placeviterbiSimply(obs, DT, obsDT):
    obs = [('始##始', 'begin')] + obs + [('末##末', 'end')]
    length = len(obs)
    for no in range(length):
        if (obs[no][1] == 'ns') and (obsDT.tree[obs[no][0]].get('total', 1001) <= 1000):
            if DT.tree.get(obs[no][0]):
                if len(obs[no][0]) <= 3:
                    DT.tree[obs[no][0]].setdefault('H', 1)
                    DT.tree[obs[no][0]].setdefault('G', 1)
                else:
                    DT.tree[obs[no][0]].update({'G': 1})
            else:
                if len(obs[no][0]) < 3:
                    DT.tree[obs[no][0]] = {'H': 1, 'G': 1}
                else:
                    DT.tree[obs[no][0]] = {'G': 1}
        elif obs[no][1].startswith('ns'):
            obs[no] = ('未##地', obs[no][1])
        elif obs[no][1].startswith('x'):
            obs[no] = ('未##串', 'x')
        elif obs[no][1].startswith('nr'):
            obs[no] = ('未##人', obs[no][1])
        elif obs[no][1].startswith('nt'):
            obs[no] = ('未##团', obs[no][1])
        elif obs[no][1].startswith('m'):
            obs[no] = ('未##数', obs[no][1])
        elif obs[no][1].startswith('t'):
            obs[no] = ('未##时', obs[no][1])
        elif not DT.tree.get(obs[no][0]):  # 不在地名词典时
            DT.tree[obs[no][0]] = {'Z': 21619956}
    path = viterbiRecognition(obs, start_p, trans_p, emit_p, DT)
    return path[1:-1]
