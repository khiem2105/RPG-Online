from collections import defaultdict

d = defaultdict(lambda: None)

for i in range(3):
    print(d[i])

for i in range(3):
    if not d[i]:
        d[i] = i

for i in range(3):
    print(d[i])

for i in d.keys():
    if d[i]:
        print(d[i])

print(d.keys())