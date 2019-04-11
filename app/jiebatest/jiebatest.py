from jieba import analyse
import re
import copy
import json

analyse.set_stop_words('stop.txt')

tfidf = analyse.extract_tags
textrank = analyse.textrank

with open("doc.txt") as fileReader:
    text = fileReader.read()

# 去除代码段
text = text.replace('\n', '')
text = text.replace('\r', '')
text = text.replace("<code>","{")
text = text.replace("</code>","}")
a1 = re.compile(r'\{.*?\}' )
text = a1.sub('',text)




kws = tfidf(text,withWeight=True)
config = {
            'name': 'Sam S Club',
            'value': 10000,
            'textStyle': {
                'normal': {
                    'color': 'black'
                },
                'emphasis': {
                    'color': 'red'
                }
            }
        }
data = {'name': '', 'value': 0}
datas = []
datas.append(config)
for kw in kws:
    data['name'] = kw[0]
    data['value'] = int(kw[1]*1000)
    datas.append(copy.deepcopy(data))
print(datas)
print(len(datas))
print('---------------------------------')
print(json.dumps(datas))
# print(kws[:3])
# print()
# for kw in kws:
#     print("{0} ".format(kw))
# print('---------------------------------')
# kws = textrank(text)
# print()
# for kw in kws:
#     print("{0} ".format(kw))