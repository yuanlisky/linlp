# -*- coding: utf-8 -*-
import os
import pickle
from linlp.compat import person, place, organization
from linlp.recognition.PlaceRecognition import *
from linlp.recognition.PersonRecognition import *
from linlp.recognition.OrganizationRecognition import *


def initialize(dictionary, temp_dir, DictTree, cachename):
    """
    初始化实体识别字典
    """
    cache_file = _setup_cache(dictionary, temp_dir, DictTree, cachename)
    if not DictTree.tree:  # 没有建立新缓存则直接从缓存载入
        with open(cache_file, 'rb') as f:
            DictTree.tree = pickle.load(f)


def _gen_pfdict(dictionary, DictTree):
    with open(dictionary, 'rb') as f:
        dict_name = f.name
        for lineno, ln in enumerate(f, 1):
            line = ln.strip()
            if not isinstance(line, str):
                try:
                    line = line.decode('utf-8')
                except UnicodeDecodeError:
                    raise ValueError('dictionary file %s must be utf-8' % dict_name)
            if not line:
                continue
            line = line.split(' ')
            DictTree.add(line)


def _setup_cache(dictionary, temp_dir, DictTree, cachename):
    """
    根据绝对路径，建立缓存
    """
    cache_file_name = "linlp." + cachename + ".cache"
    cache_file = os.path.join(temp_dir, cache_file_name)
    if os.path.isfile(cache_file) and os.path.getmtime(cache_file) > os.path.getmtime(dictionary):
        return cache_file  # 缓存文件存在，且缓存文件比字典文件要新，则不建立新缓存
    else:
        _gen_pfdict(dictionary, DictTree)
    with open(cache_file, 'wb') as f:
        pickle.dump(DictTree.tree, f)
    return cache_file


def recognition(obs, path, AC, types, debug):
    sentence = list()
    pos = list()
    res = dict()
    s = list()
    length = len(obs)
    for no in range(length):
        sentence.append(obs[no][0])
        pos.append(obs[no][1])
    match = AC.search(path)
    nexti = 0
    pattern = match.pop(0) if match else None
    while nexti < len(path):
        if pattern:
            if match:
                # 最大匹配
                if pattern[0] == match[0][0]:
                    pattern = match.pop(0)
                    continue
            if pattern[0] == nexti:
                res[pattern[0]] = (pattern[1]+1, types)
                if debug:
                    k = ''.join(path[pattern[0]:pattern[1]+1])
                    v = ''.join(sentence[pattern[0]:pattern[1]+1])
                    s.append((k, v))
                nexti = pattern[1] + 1
                while match:
                    pattern = match.pop(0)
                    if pattern[0] >= nexti:
                        break
                else:
                    pattern = None
            else:
                res[nexti] = (nexti+1, pos[nexti])
                nexti += 1
        else:
            res[nexti] = (nexti + 1, pos[nexti])
            nexti += 1
    return res, s


def personrecognition(sen, DT, obsDT, debug):
    path = personviterbiSimply(sen, DT, obsDT, debug)
    res, s = recognition(sen, path, person, 'nr', debug)
    if s:
        for word in s:
            print('识别出人名: %s %s' % (word[1], word[0]))
        print('')
    return res


def placerecognition(sen, DT, obsDT, debug):
    path = placeviterbiSimply(sen, DT, obsDT, debug)
    res, s = recognition(sen, path, place, 'ns', debug)
    if s:
        for word in s:
            print('识别出地名: %s %s' % (word[1], word[0]))
        print('')
    return res


def organizationrecognition(sen, DT, obsDT, debug):
    path = organizationviterbiSimply(sen, DT, obsDT, debug)
    res, s = recognition(sen, path, organization, 'nt', debug)
    if s:
        for word in s:
            print('识别出机构名: %s %s' % (word[1], word[0]))
        print('')
    return res


def dictadd(*args):
    fir = args[0]
    for pdict in args[1:]:
        for k, v in pdict.items():
            if k not in fir.keys():
                fir.update({k: v})
            else:
                if v[0] > fir[k][0]:
                    fir[k] = v

if __name__ == '__main__':
    pass
