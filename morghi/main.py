from itertools import chain, repeat

mylist = ['aaa', 'bbb', 'ccc']
nums = [1, 2, 2]
m = list(chain.from_iterable(map(repeat, mylist, nums)))

m = ['ddd']+m+['ddd']
print(m)
print(m.index('bbb'))
print(m)
import random
random.shuffle(m)

print(m)