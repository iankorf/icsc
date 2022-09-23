
import argparse
import datetime
import json
import os
import sys
import time

def splitdate(s):
	y, m, d = s.split('-')
	return int(y), int(m), int(d)

parser = argparse.ArgumentParser(description='publications processor')
parser.add_argument('beg', type=str, metavar='<beg>', help='begin date')
parser.add_argument('end', type=str, metavar='<end>', help='end date')
arg = parser.parse_args()

url = 'https://sci.jonudell.info/public_annos/get_public_annos?day='

y1, m1, d1 = splitdate(arg.beg)
y2, m2, d2 = splitdate(arg.end)

beg = datetime.date(y1, m1, d1)
end = datetime.date(y2, m2, d2)
delta = datetime.timedelta(days=1)

##############################
# Scicrunch Download Section #
##############################

day = beg
while day <= end:
	jfile = f'build/scicrunch/{day}.json'
	if os.path.isfile(jfile):
		day += delta
		continue
	sys.stderr.write(f'downloading scicrunch:{day}\n')
	os.system(f'wget --no-check-certificate -q "{url}{day}" -O {jfile}')
	day += delta
	time.sleep(1)

########################
# Organization Section #
########################

day = beg
papers = {} # indexed by pmid, contains a dict of rrids
while day <= end:
	with open(f'build/scicrunch/{day}.json') as fp:
		sdata = fp.read()
		if sdata.endswith('not found'):
			sys.stderr.write(f'record not found: {day}\n')
			records = []
		else:
			records = json.loads(sdata)
	for rec in records:
		if rec['vendor'] == 'MMRRC':
			pmid = rec['pmid']
			rrid = rec['rrid']
			if pmid not in papers: papers[pmid] = {}
			papers[pmid][rrid] = True
	day += delta

##########################
# MMRRC Download Section #
##########################

url = 'https://api.mmrrc.org/api/v1/catalog/getCatalogEntry/'
products = []
for pub in papers:
	for rrid in papers[pub]:
		idx, loc = rrid[11:].split('-')
		products.append(idx)
for cat in products:
	jfile = f'build/mmrrc/{cat}.json'
	if os.path.isfile(jfile): continue
	sys.stderr.write(f'downloading mmrrc:{cat}\n')
	os.system(f'wget --no-check-certificate -q "{url}{cat}" -O {jfile}')
	time.sleep(1)

###########################
# PubMed Download Section #
###########################

url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=' 

for pmid in papers:
	jfile = f'build/pubmed/{pmid}.json'
	if os.path.isfile(jfile): continue
	sys.stderr.write(f'downloading pubmed:{pmid}\n')
	os.system(f'wget --no-check-certificate -q "{url}{pmid}" -O {jfile}')
	time.sleep(1)

##################
# Output Section #
##################

m2i = {
	'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
	'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

def getdate(s):
	try:
		y, m, d = s.split(' ')
		return datetime.date(int(y), m2i[m], int(d))
	except:
		return None

def get_paper(pmid):
	with open(f'build/pubmed/{pmid}.json') as fp:
		data = json.loads(fp.read())
	uid = data['result']['uids'][0]
	source = data['result'][uid]['source']
	title = data['result'][uid]['title']
	pdate = getdate(data['result'][uid]['pubdate'])
	edate = getdate(data['result'][uid]['epubdate'])
	if pdate is not None: return title, source, pdate
	if edate is not None: return title, source, edate
	return None, None, None

def get_strain(cat):
	with open(f'build/mmrrc/{cat}.json') as fp:
		data = json.loads(fp.read())
	return data['strain_name']

# at some point they started putting in older papers...
currentpapers = {}
for pmid in papers:
	title, source, pdate = get_paper(pmid)
	if title is None:
		sys.stderr.write(f'trouble parsing pmid: {pmid}\n')
		continue
	if pdate < beg or pdate > end: continue
	currentpapers[pmid] = papers[pmid]


print('<h1>Publications</h1>')
pubmed = 'https://pubmed.ncbi.nlm.nih.gov/'
mmrrc = 'https://www.mmrrc.org/catalog/sds.php?mmrrc_id='

for pmid in currentpapers:
	title, source, pdate = get_paper(pmid)
	
	print(f'{title} <em>{source}</em>.', end=' ')
	print(f'<a href="{pubmed}{pmid}">PMID:{pmid}</a>.', end=' ')
	txt = []
	print('RRIDs:', end=' ')
	for rrid in currentpapers[pmid]:
		idx, loc = rrid[11:].split('-')
		txt.append(f'<a href="{mmrrc}{idx}">{rrid[11:]}</a>')
	print(f'{", ".join(txt)}.<br>')

print('<h1>Products</h1>')
rrids = {}
for pmid in currentpapers:
	for rrid in currentpapers[pmid]:
		if rrid not in rrids: rrids[rrid] = 0
		rrids[rrid] += 1
for k, v in sorted(rrids.items(), key=lambda item: item[1], reverse=True):
	idx, loc = k[11:].split('-')
	print(f'<a href="{mmrrc}{idx}">{k}</a> ({v}) {get_strain(idx)}<br>')


sys.stderr.write(f'{len(currentpapers)} papers, {len(rrids)} products\n')
