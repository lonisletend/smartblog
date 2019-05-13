# import jieba
from jieba import cut

str = 'jieba.cut_for_search 方法接受两个参数：需要分词的字符串；是否使用 HMM 模型。该方法适合用于搜索引擎构建倒排索引的分词，粒度比较细'
filter_dict_list = ['参数', '适合', '666']
seg_list = cut(str, cut_all=False)
sense_list = list(set(filter_dict_list).intersection(set(seg_list)))
# print(list(seg_list))
print(sense_list)
for word in sense_list:
    str = str.replace(word, '*'*len(word))
print(str)


filter_dict = []
file = open('sense.txt')
while 1:
    line = file.readline()
    if not line:
        break
    filter_dict.append(line.replace('\n',''))
print(filter_dict[594:620])


