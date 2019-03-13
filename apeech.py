import os
from itertools import groupby
from collections import namedtuple
os.system("python 3.py")
os.system("autosub file.wav")
filename="file.srt"
with open(filename) as f:
    res = [list(g) for b,g in groupby(f, lambda x: bool(x.strip())) if b]
Subtitle = namedtuple('Subtitle', 'number start end content')

subs = []

for sub in res:
    if len(sub) >= 3:
        sub = [x.strip() for x in sub]
        number, start_end, content = sub
        start, end = start_end.split(' --> ')
        subs.append(content)
#print(subs)
x=[]
for i in subs:
    print(i)
    if(i.find("Vodafone")+1):
        x.append("Vodafone")
    if(i.find("Airtel")+1):
        x.append("Airtel")
    if(i.find("Cadbury")+1):
        x.append("Cadbury")
print(x)
