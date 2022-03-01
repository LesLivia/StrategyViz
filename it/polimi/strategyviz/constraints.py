import matplotlib.pyplot as plt

f = open('./resources/strategies/lead.txt')
lines = f.readlines()
lines = [l for l in lines if l.startswith('State:')]

dist_lines = [l.split('h_dd=')[1].split(' ')[0] for l in lines]
dist_values = [(i, int(l)) for i, l in enumerate(dist_lines)]
dist_values = sorted(dist_values, key=lambda tup: tup[1])

ftg_lines = [l.split('h_df=')[1].split(' ')[0] for l in lines]
ftg_values = [(i, int(l)) for i, l in enumerate(ftg_lines)]

data = []
for tup in dist_values:
    corresponding_ftg = [tup2[1] for tup2 in ftg_values if tup2[0] == tup[0]][0]
    data.append((tup[1], corresponding_ftg))

plt.figure()
plt.plot([x[0] for x in data], [x[1] for x in data])
plt.show()
