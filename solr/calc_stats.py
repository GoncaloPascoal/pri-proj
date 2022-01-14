
rel_50 = 27
top_10_str = 'YYNYYYYNYN' # 1
#top_10_str = 'YYYYYYYNYN' # 2
#top_10_str = 'NYYYYYYYYY' # 3
#top_10_str = 'YNYYYNNYNY' # 4
#top_10_str = 'NYYYYYYYYY' # 5
#top_10_str = 'YYYYYYYYYN' # 6

#top_10_str = 'NYYYYYYYYYYYYYYNY' # 5

rel = 0
total = 0
pk = []
rk = []
ap = []

for c in top_10_str:
    total += 1
    if c == 'Y':
        rel += 1
        ap.append(rel / total)
    pk.append(rel / total)
    rk.append(rel / rel_50)

pk = list(map(lambda x: round(x, 3), pk))
rk = list(map(lambda x: round(x, 3), rk))

for r, p in zip(rk, pk):
    print(r, p)

print('P@5:', pk[4])
print('P@10:', pk[9])
print('Avg. Precision:', round(sum(ap) / len(ap), 3))
print('Recall (top 50):', round(15 / rel_50, 3))