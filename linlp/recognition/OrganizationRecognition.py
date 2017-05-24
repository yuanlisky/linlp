# -*- coding: utf-8 -*-
from linlp.algorithm.Viterbi import viterbiRecognitionSimply
from linlp.algorithm.viterbiMat.prob_trans_organization import prob_trans as trans_p
from linlp.algorithm.viterbiMat.prob_emit_organization import prob_emit as emit_p


def organizationviterbiSimply(obs, DT, obsDT, debug):
    if debug:
        x = obs
    obs = [('始##始', 'begin')] + obs + [('末##末', 'end')]
    switch = {'nz': 1, 'ni': 2, 'nic': 2, 'nis': 2, 'nit': 2, 'm': 3}
    length = len(obs)
    for no in range(length):
        case = switch.get(obs[no][1], 0)
        if not DT.tree.get(obs[no][0]):
            DT.tree[obs[no][0]] = dict()
        if case == 1:
            if obsDT.tree[obs[no][0]].get('total', 1001) <= 1000:
                DT.tree[obs[no][0]].setdefault('F', 1000)
            else:
                DT.tree[obs[no][0]].setdefault('Z', 21149365)
        elif case == 2:
            DT.tree[obs[no][0]].setdefault('K', 1000)
            DT.tree[obs[no][0]].setdefault('D', 1000)
        elif case == 3 and len(obsDT.tree.get(obs[no][0], 'm')) != 2:
            DT.tree[obs[no][0]] = {'M': 1000}
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
        elif not DT.tree.get(obs[no][0]):  # 不在机构词典时
            DT.tree[obs[no][0]] = {'Z': 21149365}
    path = viterbiRecognitionSimply(obs, trans_p, emit_p, DT)
    if debug:
        s = ''
        t = '['
        l = len(x)
        for i in range(l):
            word = x[i]
            s += '[' + word[0] + ' '
            t += word[0]
            for k, v in DT.tree[obs[i+1][0]].items():
                if k == 'total':
                    continue
                s += k + ':' + str(v) + ' '
            s += ']'
            t += '/' + path[i+1] + ', '
        t += ']'
        print('机构名角色观察: %s' % s)
        print('机构名角色标注: %s' % t)
    return path[1:-1]
