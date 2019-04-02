from jieba import analyse
import re

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




kws = tfidf(text)
print()
for kw in kws:
    print("{0} ".format(kw))
# print('---------------------------------')
# kws = textrank(text)
# print()
# for kw in kws:
#     print("{0} ".format(kw))