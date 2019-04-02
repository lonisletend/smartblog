import re
import sys

s='{通配符}你好，今天开学了{通配符},你好'
print("s", s)
a1 = re.compile(r'\{.*?\}' )
d = a1.sub('',s)
print("d",d)
a1 = re.compile(r'\{[^}]*\}' )
d = a1.sub('',s)
print("d",d)