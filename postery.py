import csv

faves = ['Sleep', 'Dementia', 'Circadian', 'Alzheimer']

mesht = {}
with open('pmid_meshTerms.csv') as fp:
	reader = csv.reader(fp, delimiter=',', quotechar='"')
	for mid, pid, mesh in reader:
		keep = False
		for fave in faves:
			if fave in mesh:
				keep = True
				break
		if keep: mesht[mid] = mesh



with open('strain.csv') as fp:
	reader = csv.reader(fp, delimiter=',', quotechar='"')
	for f in reader:
		mid = f[0]
		nom = f[2]
		ava = f[5]
		if ava == 'Currently Unavailable': continue
		if mid in mesht:
			print(mid, nom, mesht[mid])
