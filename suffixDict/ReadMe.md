## 地址信息词条切分程序说明

版本：1.0

描述：实现分词初步目的，分词结果中包含目标词条信息(达标比率待测)

完成时间：2017.02.27

### 1. 环境配置

操作系统：64位windows 7

处理器：Intel(R) Core(TM) i5 CPU

内存(RAM)：4G

Python版本：Python 3.5.2

Java自然语言处理包HanLP：[Hanlp-1.3.2.jar](https://github.com/hankcs/HanLP/releases)

HanLP词典和模型数据包：[Data-for-1.3.2.zip](http://115.159.41.123/files/data-for-1.3.2.zip)，需将数据包解压出的data文件夹放入jar包所在文件夹下

### 2. 程序说明

共有3个. py文件

`useHanLP_seg.py`

`useHanLP_segPro.py`

`suffix_result.py`

目标：句子中取出全文地址，目前实现功能为结果集中包含目标地址信息词条。

#### 1) `useHanLP_seg.py`

使用Python调用自然语言处理包HanLP，对原始地址信息样本进行初步分词。

封装类：

	HanLPseg( javapath, javafile)

类初始化参数：

	javapath：Java自然语言处理包HanLP所在文件夹路径，例javapath='C:\hanlp'
	javafile：Java自然语言处理包HanLP存放路径，例javafile='C:\hanlp\hanlp-1.3.2.jar'

方法：

	HanLPseg.seg(sourcefile, resultfile, model='N', linenum=None)

方法参数：

	sourcefile: 源文件，地理信息样本，编码为utf-8
	resultfile: 结果文件，使用HanLP分词器分词后结果，编码为utf-8，词语后有换行符'\n'
	model: 分词模式，'P': 开启地址识别；'O': 开启机构识别；'A': 两种识别都开启；'N': 默认模式，都不开启
	linenum: 读取源文件前linenum行地理信息
	return: 无返回，生成分词结果文件resultfile

样例：
```python
s = HanLPseg(javapath='C:\hanlp', javafile='C:\hanlp\hanlp-1.3.2.jar')
s.seg('./dictionary/BJplace.txt', './B1.txt', model='P', linenum=100)
```
说明：
Java包路径为`'C:\hanlp\hanlp-1.3.2.jar'`，存放在`'C:\hanlp'`中，所使用的样本文件为`'./dictionary/BJplace.txt'`，生成文件`'./B1.txt'`，模式`model='P'`表示开启地址识别，`linenum=100`表示只读取样本信息文件前100行进行分词。

结果演示：

	北京市房山区窦店镇于庄锦绣路18号
	北京市房山区青龙湖镇豆各庄村下四区43号

输出：

	北京市/ns
	房山/ns
	区
	窦店镇/ns
	于庄/ns
	锦绣路/ns
	号
	青龙湖镇/ns
	豆各庄村/ns
	下
	四

#### 2) `useHanLP_segPro.py`

处理Java包HanLP的分词结果，输出结果为地名词典：
① 过滤N个字的词语(可设置N)；
② 选择词性为`['ns'，'nsf'，'nz']`的词语(可设置选择词性种类)。

封装类：

	SegPro( )

方法1：

	SegPro.process(sourcefile, resultfile, tag, filterlength=1)

方法1参数

	sourcefile: HanLP分词结果文件，编码为utf-8
	resultfile: 对HanLP分词结果进行处理，输出的txt文件，编码为utf-8，词语后有换行符'\n'
	tag: 选择词性为tag的词语，tag为可迭代数据类型，一般为列表
	filterlength: 过滤长度为filterlength的词语
	return: 返回对HanLP分词结果进行处理地名文件resultfile

方法2：

	SegPro.tagging_filter(s, tag )

方法2参数：

	s: 样本词条
	tag: 词性，为可迭代数据类型，一般为列表
	return: 若样本词条中包含tag中的词性，则返回1，否则返回0

样例：
```python
tag = ['/nt', '/nz', '/ns', '/nsf']
segpro = SegPro()
segpro.process('./result/BJplacePro.txt', './BJ1.txt', tag, filterlength=1)
```
说明：
首先定义好词性`tag`列表，源文件`'./result/BJplacePro.txt'`为Java包HanLP分词后输出的结果，`'./BJ1.txt'`为处理结果，地名词典文件，`tag`为需要选择的词性，`filterlength=1`表示过滤一个字的词语。

结果演示：

	北京市/ns
	房山/ns
	区
	窦店镇/ns
	于庄/ns
	锦绣路/ns
	号
	青龙湖镇/ns
	豆各庄村/ns
	下
	四

输出：

	北京市/ns
	房山/ns
	窦店镇/ns
	于庄/ns
	锦绣路/ns
	青龙湖镇/ns
	豆各庄村/ns

#### 3) suffix_result.py
利用地名词典文件，以及总结的后缀词典，对原始地址信息样本进行切分。设原始地址信息样本中有词条A，实现过程为：
① 搜索A在地名词典中的最大正向匹配a；
② 倒序搜索a后N个字符是否有字符串s包含在后缀词典中，搜索范围N为随机确定，目前暂定为7；
③ 将a至s及中间的字符串拼接，组成新词条。
最后得到地址信息词条切分文件。

封装类：

	buildDict( )

方法1：

	buildDict. loadfile(f)

方法1参数：

	f: 要载入的词典文件，编码为utf-8
	return: 将词典文件按行保存到Python字典中

方法2：

	buildDict. gen_longest(dt)

方法2参数：

	dt: 存有词条数据的Python字典
	return: 返回最长词条的长度

方法3：

	buildDict. gen_pfdict(f)

方法3参数：

	f: 要载入的词典文件，，编码为utf-8
	return: 按词典文件建立前缀字典，保存到Python字典中，返回此字典

方法4：

	buildDict. gen_dict( sourcefile, dictfile, suffixfile, resultfile, linenum=None, lensuffix=7)

方法4参数：

	sourcefile: 原始地址信息样本文件，编码为utf-8
	dictfile: 地名词典文件，编码为utf-8
	suffixfile: 后缀字典文件，编码为utf-8
	resultfile: 结果输出文件，编码为utf-8，换行符为'\n'
	linenum: 处理原始地址信息样本文件前linenum行
	lensuffix: 正向最大匹配词语向后搜索后缀的位数
	return: 生成结果输出文件resultfile

样例：
```python
DT = buildDict()
DT.gen_dict(sourcefile='./dictionary/BJplace.txt',
	dictfile='./result/BJplaceDone.txt', 
	suffixfile='./dictionary/classify.txt', 
	resultfile='classify_result1.txt', 
	linenum=1000)
```
说明：
原始地址信息样本文件为`'./dictionary/BJplace.txt'`，地名词典为`'./result/BJplaceDone.txt'`，后缀词典为`'./dictionary/classify.txt'`，结果输出文件为`resultfile`，只处理原始地址信息样本文件前1000行，正向最大匹配词语向后搜索后缀的位数为默认的7位。
结果演示：

	北京市房山区窦店镇于庄锦绣路18号
	北京市房山区青龙湖镇豆各庄村下四区43号

输出：

	['北京市房山区', '房山区窦店镇于庄', '窦店镇于庄锦绣路', '于庄锦绣路18号', '锦绣路18号']
	['北京市房山区', '房山区青龙湖镇豆各庄', '青龙湖镇豆各庄村下四区', '豆各庄村下四区43号', '四区43号']
