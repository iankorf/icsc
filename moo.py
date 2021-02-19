from pandas import read_csv
import sys
import math
import json

## HIV-1, human interaction database
hint = []
with open('HIVinteractions.txt') as fp:
	header = fp.readline()
	for line in fp.readlines():
		f = line.split('\t')
		tax = f[0]
		gid = f[5]
		if tax != '9606': continue
		hint.append(gid)
sys.stderr.write(f'HIV interactions: {len(hint)}\n')

## MGI HomoloGene
mgi = {}
with open('HOM_AllOrganism.rpt.txt') as fp:
	header = fp.readline()
	for line in fp.readlines():
		f = line.split('\t')
		hid = f[0]
		org = f[1]
		gid = f[3]
		oid = f[7]
		if org == 'mouse, laboratory':
			if hid not in mgi: mgi[hid] = {} 
			mgi[hid]['mouse'] = gid
		elif org == 'human':
			if hid not in mgi: continue
			mgi[hid]['human'] = gid
			mgi[hid]['omim'] = oid
sys.stderr.write(f'MGI homologenes: {len(mgi)}\n')

h2m = {}
m2h = {}
h2o = {}
for rec in mgi:
	if len(mgi[rec].values()) == 3:
		mid, hid, oid = mgi[rec].values()
		m2h[mid] = hid
		h2o[hid] = oid
		h2m[hid] = mid

# MMRRC Catalog
df = read_csv('mmrrc_catalog_data.csv', header=1, dtype=str)
g2m = {}
m2g = {}
for row in df.values:
	mid = row[0]
	gid = row[10]
	if type(gid) == float and math.isnan(gid): continue
	if gid not in g2m: g2m[gid] = []
	if mid not in m2g: m2g[mid] = []
	g2m[gid].append(mid)
	m2g[mid].append(gid)
sys.stderr.write(f'MMRRC strains with human orthologs: {len(m2g)}\n')

# discovery loop
keep = {}
for hid in hint:
	if hid not in h2m: continue
	mid = h2m[hid]
	oid = h2o[hid]
	if mid in g2m:
		for strain in g2m[mid]:
			if strain not in keep: keep[strain] = []
			keep[strain].append((mid, hid, oid))

out = []
for strain in keep:
	out.append(f'{strain} {keep[strain]}')
sys.stderr.write(f'MMRRC strains with possible HIV interactions: {len(out)}\n')

for line in out: print(line)



"""

"""