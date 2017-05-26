# -*- coding: utf-8 -*-
"""
主分词器：
    使用自定义词典建立前缀词典
    添加自定义词典到默认词典生成的前缀词典
    更新缓存文件
    更新前缀词典
    完成基本分词
"""
import math
import time
import tempfile
from hashlib import md5
from linlp.compat import *
from linlp.log import logger
from linlp.algorithm import Viterbi
from linlp.recognition.Recognition import *


class Segment(object):
    def __init__(self):
        """初始化类属性"""
        self.DT = DictTree()
        self.PersonDict = DictTree()
        self.PlaceDict = DictTree()
        self.OrganizationDict = DictTree()
        # 字典绝对路径(python格式)
        self.default_dictionary = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dict.txt'))
        self.dictionary = self.default_dictionary
        self.FREQ = dict()  # 前缀词典
        self.total = 0
        self.temp_dir = tempfile.gettempdir()  # 缓存路径
        self.cache_file = None
        self.initialized = False
        self.cached = False
        self.POS = False
        self.HMM = False
        self.personrecognition = False
        self.placerecognition = False
        self.organizationrecognition = False
        self.debug = False

    def __repr__(self):
        return '<Initialization dictionary = %r>' % self.dictionary

    def initialize(self):
        """
        初始化，作用为加载词典数据
        若主词典文件的最后修改时间早于缓存的建立时间
        则不建立新的缓存，直接从已存在的缓存文件中加载词典数据
        """
        self._setup_cache()
        if not self.cached:  # 没有建立新缓存则直接从缓存载入
            logger.debug("Loading prefix dict from the cache: %s ..." % self.cache_file)
            t1 = time.time()
            with open(self.cache_file, 'rb') as f:
                self.FREQ, self.total, self.DT.tree = pickle.load(f)
            t = time.time() - t1
            logger.debug("Loading model cost %.3f seconds." % t)
        logger.debug("Prefix dict has been built successfully!")
        self.initialized = True

    def set_dictionary(self, dictionary=None):
        """
        设置主词典
        参数:
            - dictionary: 主词典文件的完整路径，当不指定时为使用默认词典
        词典结构：
            词语1 词性1 频数1 词性2 频数2 ...
            词语2 词性1 频数1 词性2 频数2 ...
            
            中间以空格隔开，或者
            
            词语1
            词语2
            只有词语，不指定词性和频数
            那么词性默认为'nz'，频数由suggest_freq计算
        """
        self.FREQ = dict()
        self.total = 0
        self.dictionary = os.path.abspath(dictionary) if dictionary else self.default_dictionary
        self.initialize()

    def add_dictionary(self, dictionary):
        """
        添加词典到主词典生成的词典数据中
        参数：
            - dictionary: 词典文件的完整路径，将文件中的词语、词性、频数，添加到内存的词典数据中
        词典结构：
            同主词典
        """
        self.check_initialized()
        dictionary = os.path.abspath(dictionary)
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
                word = line[0]
                if len(line) == 1:
                    freq = self.suggest_freq(word)
                    tag = 'nz'
                    line = [word, tag, freq]
                self.DT.add(line)
                freq = self.DT.tree[line[0]]['total']
                self._update_pfdict(word, freq)

    def _gen_pfdict(self):
        """
        使用主词典，建立词典数据
        """
        with open(self.dictionary, 'rb') as f:
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
                word = line[0]
                if len(line) == 1:
                    freq = self.suggest_freq(word)
                    tag = 'nz'
                    line = [word, tag, freq]
                self.DT.add(line)
                freq = self.DT.tree[line[0]]['total']
                self._update_pfdict(word, freq)

    def _update_pfdict(self, word, freq):
        """
        更新词典数据
        参数：
            - word: 加入前缀词典的词语，str类型
            - freq: 加入词语的频数，int类型
        """
        try:
            if self.FREQ.get(word, 0):  # word 在FREQ中
                wfreq = self.FREQ[word]
                self.total += freq - wfreq
            else:
                self.total += freq
            self.FREQ[word] = freq
            for ch in range(len(word)):
                wfrag = word[:ch+1]
                if wfrag not in self.FREQ:
                    self.FREQ[wfrag] = 0
        except ValueError:
            raise ValueError(
                'invalid word: "%s %s"' % (word, freq))

    def _setup_cache(self):
        """
        若缓存文件已存在且最后修改时间早于主词典，则不建立新缓存数据
        否则根据主词典，建立词典数据，并将数据存入新建缓存中
        """
        cache_file_name = "linlp.cache" \
            if self.dictionary == self.default_dictionary \
            else "linlp.u%s.cache" % md5(self.dictionary.encode('utf-8', 'replace')).hexdigest()
        self.cache_file = os.path.join(self.temp_dir, cache_file_name)
        if os.path.isfile(self.cache_file) and os.path.getmtime(self.cache_file) > os.path.getmtime(self.dictionary):
            logger.debug("Cache file %s is exists..." % os.path.abspath(self.cache_file))
            return  # 缓存文件存在，且缓存文件比字典文件要新，则不建立新缓存
        else:
            logger.debug("Building prefix dict from the main dictionary: %s ..." % self.dictionary)
            t1 = time.time()
            self._gen_pfdict()
            t = time.time() - t1
            logger.debug("Building model cost %.3f seconds." % t)
        logger.debug("Dumping model to file cache %s" % os.path.abspath(self.cache_file))
        with open(self.cache_file, 'wb') as f:
            pickle.dump((self.FREQ, self.total, self.DT.tree), f)
            self.cached = True
        return  # 建立了新缓存文件

    def add_word(self, word, tag=None, freq=None):
        """
        动态添加词语，临时添加，结束程序即消除(将单词加入内存中的词典数据)
        参数：
            - word: 加入词典数据的词语，str类型
            - tag: 加入词语的词性，str类型
            - freq: 加入词语的频数，int类型
        """
        self.check_initialized()
        freq = int(freq) if freq is not None else self.suggest_freq(word)
        self._update_pfdict(word, freq)  # 更新前缀词典
        # 更新核心词典DictTree
        if not self.DT.tree.get(word):
            if tag:
                self.DT.add([word, tag, freq])
            else:
                self.DT.add([word, 'nz', freq])

    def del_word(self, word):
        """
        从词典数据中删除词语
        参数：
            - word: 要删除的词语，str类型
        """
        self.add_word(word, freq=0)
        if self.DT.tree.get(word):
            del(self.DT.tree[word])

    def suggest_freq(self, word):
        """
        添加的词语推荐频数
        参数：
            - word: 加入前缀词典的词语，str类型
        """
        self.check_initialized()
        ftotal = float(self.total)
        freq = 1
        flag = self.HMM
        self.HMM = False
        for seg in self.cut(word):
            freq *= self.FREQ.get(seg, 1) / ftotal  # 所有成词情况的概率积,word = '中关村北大街'，p('中关村')*P('北大街')
        freq = max(int(freq * self.total) + 1, self.FREQ.get(word, 1))
        self.HMM = flag
        return freq

    def set_temp_dir(self, path=tempfile.gettempdir()):
        """
        设置缓存路径
        参数：
            - path: 缓存的路径，路径格式，默认设置为系统缓存路径
        """
        if not os.path.isdir(path):
            os.makedirs(path)
            logger.debug("Directory '%s' has been created." % path)
        if self.temp_dir != os.path.abspath(path):
            self.temp_dir = os.path.abspath(path)
            self.initialized = False
        logger.debug("The cache file directory is changed to: %s ..." % self.temp_dir)

    def check_initialized(self):
        """
        检查是否初始化，若未初始化，则进行初始化，加载词典数据
        """
        if not self.initialized:
            self.initialize()

    def _get_DAG(self, sentence):
        """
        根据前缀词典，获取句子sentence的有向无环图
        """
        self.check_initialized()
        DAG = dict()
        N = len(sentence)
        for k in range(N):
            tmplist = list()
            i = k
            frag = sentence[k]
            while i < N and frag in self.FREQ:
                if self.FREQ[frag]:
                    tmplist.append(i)
                i += 1
                frag = sentence[k:i + 1]
            if not tmplist:
                tmplist.append(k)
            DAG[k] = tmplist
        return DAG

    def _calc(self, sentence, DAG):
        """
        计算句子所生成有向无环图的最大概率路径
        参数：
            - sentence: 待分词的句子，str类型
            - DAG: sentence的有向无环图
        返回：
            - route: 记录sentence的有向无环图的最大概率路径，dict类型
        """
        N = len(sentence)
        route = dict()
        route[N] = (0, 0)
        logtotal = math.log(self.total)
        for idx in range(N-1, -1, -1):  # 从后往前遍历每个分词
            route[idx] = max((math.log(self.FREQ.get(sentence[idx:x+1]) or 1) -
                              logtotal+route[x+1][0], x) for x in DAG[idx])  # 取log防止向下溢出,取过log后除法变为减法
        return route

    def __cut_NO_HMM(self, sentence):
        """
        根据前缀词典进行最大概率路径分词，并切分出英文字符串和数字
        """
        DAG = self._get_DAG(sentence)
        route = self._calc(sentence, DAG)
        x = 0
        N = len(sentence)
        buf = ''
        while x < N:
            y = route[x][1] + 1  # x到y组合成词概率最大 route = {start: (prob, end)}
            l_word = sentence[x:y]
            # <editor-fold desc="将英文字符串或数字合并">
            if re_eng.match(l_word) or (l_word == '.') or (l_word == '-') or (l_word == '+'):
                if buf == '' and l_word != '.':
                    buf += l_word
                    x = y
                elif re_en.match(buf) and re_en_1.match(l_word):
                    buf += l_word
                    x = y
                elif re_num.match(buf) and (re_num_1.match(l_word) or (l_word == '.')):
                    buf += l_word
                    x = y
                elif re_num_f.match(buf) and re_num_1.match(l_word):
                    buf += l_word
                    x = y
                else:
                    if buf:
                        yield buf
                        buf = ''
                        buf += l_word
                        x = y
            else:
                if buf:
                    yield buf
                    buf = ''
                yield l_word
                x = y
            # </editor-fold>
        if buf:
            yield buf

    @staticmethod
    def __cut_viterbi(sentence):
        """
        按'BMES'标注将句子切分 
        """
        pos_list = Viterbi.viterbi(sentence, 'BMES')
        begin, nexti = 0, 0
        for i, char in enumerate(sentence):
            pos = pos_list[i]
            if pos == 'B':
                begin = i
            elif pos == 'E':
                yield sentence[begin:i + 1]
                nexti = i + 1
            elif pos == 'S':
                yield char
                nexti = i + 1
        if nexti < len(sentence):
            yield sentence[nexti:]

    def __cut_use_viterbi(self, sentence):
        """
        将句子粗分,按汉字非汉字分一次，汉字部分进行'BMES'切分，非汉字部分按空格或换行符切分
        """
        blocks = re_han_cut_all.split(sentence)  # 把汉字和非汉字分开
        for blk in blocks:
            if re_han_cut_all.match(blk):  # 如果是汉字
                for word in self.__cut_viterbi(blk):
                    yield word
            else:  # 不是汉字
                tmp = re_skip_default.split(blk)  # 按空格或换行符切分blk
                for x in tmp:
                    if x:
                        yield x

    def __cut_HMM(self, sentence):
        """
        在按最大概率路径分词的基础上，根据标注'BMES'对未登录词进行HMM分词
        """
        DAG = self._get_DAG(sentence)
        route = self._calc(sentence, DAG)
        x = 0
        buf = ''
        N = len(sentence)
        while x < N:
            y = route[x][1] + 1
            l_word = sentence[x:y]
            if y - x == 1:
                buf += l_word
            else:
                if buf:
                    if len(buf) == 1:
                        yield buf
                        buf = ''
                    else:
                        # 由单字组成的片段不在前缀词典中，则做viterbi
                        if not self.FREQ.get(buf):
                            recognized = self.__cut_use_viterbi(buf)
                            for t in recognized:
                                yield t
                        else:
                            for elem in buf:
                                yield elem
                        buf = ''
                yield l_word
            x = y
        if buf:
            if len(buf) == 1:
                yield buf
            elif not self.FREQ.get(buf):
                recognized = self.__cut_use_viterbi(buf)
                for t in recognized:
                    yield t
            else:
                for elem in buf:
                    yield elem

    def __cut_pos(self, sentence, func):
        sen = func(sentence)  # 按HMM分词或非HMM分词
        path = Viterbi.viterbiSimply(sen, self.DT)
        buf = ''
        num = ''
        for no, word in enumerate(func(sentence)):
            if re_num_cn.fullmatch(word) or path[no] == 'm' or re_num_f.fullmatch(word):  # 识别数字
                if buf:
                    if self.POS:
                        yield (buf, 'x')
                    else:
                        yield buf
                    buf = ''
                num += word
                continue
            else:
                if num:
                    if self.POS:
                        yield (num, 'm')
                    else:
                        yield num
                    num = ''
            if path[no] == 'x':  # 未登陆词(也包括符号、字母等不在词典内的字符)
                buf += word
            else:
                if buf:
                    if self.POS:
                        yield (buf, 'x')
                    else:
                        yield buf
                    buf = ''
                if self.POS:
                    yield (word, path[no])
                else:
                    yield word
        if num:
            if self.POS:
                yield (num, 'm')
            else:
                yield num
        if buf:
            if self.POS:
                yield (buf, 'x')
            else:
                yield buf

    def __cut_for_basic(self, sentence):
        if self.HMM:
            for word in self.__cut_pos(sentence, self.__cut_HMM):
                yield word
        else:
            for word in self.__cut_pos(sentence, self.__cut_NO_HMM):
                yield word

    def __cut_for_recognition(self, sentence):
        flag = self.POS
        self.POS = True
        sen = list(self.__cut_pos(sentence, self.__cut_NO_HMM))
        if self.debug:
            print('粗分结果: ', sen, '\n')
        self.POS = flag
        r = dict()
        sign = 0
        if self.personrecognition:
            res_person = personrecognition(sen, self.PersonDict, self.DT, self.debug)
            dictadd(r, res_person)
            sign += 1
        if self.placerecognition:
            res_place = placerecognition(sen, self.PlaceDict, self.DT, self.debug)
            dictadd(r, res_place)
            sign += 2
        if self.organizationrecognition:
            if sign == 0:
                res_person = personrecognition(sen, self.PersonDict, self.DT, self.debug)
                res_place = placerecognition(sen, self.PlaceDict, self.DT, self.debug)
                dictadd(r, res_person)
                dictadd(r, res_place)
            elif sign == 1:
                res_place = placerecognition(sen, self.PlaceDict, self.DT, self.debug)
                dictadd(r, res_place)
            elif sign == 2:
                res_person = personrecognition(sen, self.PersonDict, self.DT, self.debug)
                dictadd(r, res_person)
            y = 0
            buf = ''
            org_list = list()
            while y < len(sen):
                for p in range(y, r[y][0]):
                    buf += sen[p][0]
                org_list.append((buf, r[y][1]))
                buf = ''
                y = r[y][0]
            res_organization = organizationrecognition(org_list, self.OrganizationDict, self.DT, self.debug)
            r = res_organization
            sen = org_list
        y = 0
        buf = ''
        while y < len(sen):
            for p in range(y, r[y][0]):
                buf += sen[p][0]
            if self.POS:
                yield (buf, r[y][1])
            else:
                yield buf
            buf = ''
            y = r[y][0]

    def cut(self, sentence):
        """
        主要分词函数，根据设置对句子进行分词，返回生成器
        参数：
            - sentence: 待分词的句子，str类型
        """
        if self.personrecognition or self.placerecognition or self.organizationrecognition:
            for word in self.__cut_for_recognition(sentence):
                yield word
        else:
            for word in self.__cut_for_basic(sentence):
                yield word

    def lcut(self, *args, **kwargs):
        """
        以列表形式返回cut的分词结果
        """
        return list(self.cut(*args, **kwargs))

    def __cut_all(self, sentence):
        dag = self._get_DAG(sentence)
        old_j = -1
        for k, L in iter(dag.items()):
            if len(L) == 1 and k > old_j:
                yield sentence[k:L[0] + 1]
                old_j = L[0]
            else:
                for j in L:
                    if j > k:
                        yield sentence[k:j + 1]
                        old_j = j

    def cut_for_all(self, sentence):
        """
        全模式分词，把句子中所有的可以成词的词语都扫描出来，返回生成器
        参数：
            - sentence: 待分词的句子，str类型
        """
        blocks = re_han_cut_all.split(sentence)  # 切割成汉字，非汉字
        for blk in blocks:
            if not blk:
                continue
            if re_han_cut_all.match(blk):  # 如果是汉字
                for word in self.__cut_all(blk):
                    yield word
            else:
                tmp = re_skip_cut_all.split(blk)  # 不匹配字母，数字，井号，换行符
                for x in tmp:
                    if re_skip_cut_all.match(x):
                        yield x
                    else:
                        yield x

    def lcut_for_all(self, *args, **kwargs):
        """
        以列表形式返回cut_for_all的分词结果
        """
        return list(self.cut_for_all(*args, **kwargs))

    def cut_for_search(self, sentence):
        """
        搜索模式分词，对采用HMM分词的结果中的长词再次进行切分，返回生成器
        参数：
            - sentence: 待分词的句子，str类型
        """
        flag = self.HMM
        self.HMM = True
        words = self.cut(sentence)
        self.HMM = flag
        for w in words:
            if len(w) > 2:
                for i in range(len(w) - 1):
                    gram2 = w[i:i + 2]
                    if self.FREQ.get(gram2):
                        yield gram2
            if len(w) > 3:
                for i in range(len(w) - 2):
                    gram3 = w[i:i + 3]
                    if self.FREQ.get(gram3):
                        yield gram3
            yield w

    def lcut_for_search(self, *args, **kwargs):
        """
        以列表形式返回cut_for_search的分词结果
        """
        return list(self.cut_for_search(*args, **kwargs))

    def enable_HMM(self, boolean=True):
        """
        开关HMM分词，主要用于识别未登录词
        参数：
            - boolean: True->开启；False->关闭 
        """
        self.HMM = boolean

    def enable_personrecognition(self, boolean=True):
        """
        开关人名识别
        参数：
            - boolean: True->开启；False->关闭
        """
        self.personrecognition = boolean
        if boolean and (not self.PersonDict.tree):
            person_dictionary = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                'algorithm/viterbiMat/dictionary/person/nr.txt'))
            initialize(person_dictionary, self.temp_dir, self.PersonDict, 'person')

    def enable_placerecognition(self, boolean=True):
        """
        开关地名识别
        参数：
            - boolean: True->开启；False->关闭
        """
        self.placerecognition = boolean
        if boolean and (not self.PlaceDict.tree):
            place_dictionary = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               'algorithm/viterbiMat/dictionary/place/ns.txt'))
            initialize(place_dictionary, self.temp_dir, self.PlaceDict, 'place')

    def enable_organizationrecognition(self, boolean=True):
        """
        开关机构名识别
        参数：
            - boolean: True->开启；False->关闭
        """
        self.organizationrecognition = boolean
        if boolean:
            if not self.personrecognition:
                self.enable_personrecognition()
                self.personrecognition = False
            if not self.placerecognition:
                self.enable_placerecognition()
                self.placerecognition = False
            if not self.OrganizationDict.tree:
                organization_dictionary = os.path.abspath(os.path.join(
                                                          os.path.dirname(__file__),
                                                          'algorithm/viterbiMat/dictionary/organization/nt.txt'))
                initialize(organization_dictionary, self.temp_dir, self.OrganizationDict, 'organization')

    def enable_all(self, boolean=True):
        """
        一次开关所有实体识别
        参数：
            - boolean: True->开启；False->关闭
        """
        self.enable_personrecognition(boolean)
        self.enable_placerecognition(boolean)
        self.enable_organizationrecognition(boolean)

    def enable_POS(self, boolean=True):
        """
        开关词性标注
        参数：
            - boolean: True->开启；False->关闭
        """
        self.POS = boolean

    def enable_debug(self, boolean=True):
        """
        开关打印debug信息
        参数：
            - boolean: True->开启；False->关闭
        """
        self.debug = boolean

    @staticmethod
    def enable_log(boolean=True):
        """
        开关显示log信息
        参数：
            - boolean: True->开启；False->关闭
        """
        if boolean:
            logger.setLevel(1)
        else:
            logger.setLevel(0)

if '__main__' == __name__:
    a = Segment()
    a.enable_log(False)
    s = '朝阳区崔各庄乡来广营东路费家村西北口20米'
    a.enable_organizationrecognition()
    print(a.lcut(s))
