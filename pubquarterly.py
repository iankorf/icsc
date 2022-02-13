
import argparse
import datetime
import json
import os
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

####################
# Download Section #
####################

while beg <= end:
	jfile = f'build/scicrunch/{beg}.json'
	if os.path.isfile(jfile):
		beg += delta
		continue
	print('downloading', beg)
	os.system(f'wget --no-check-certificate -q "{url}{beg}" -O {jfile}')
	beg += delta
	time.sleep(1)

########################
# Organization Section #
########################

beg = datetime.date(y1, m1, d1)
papers = {}
rrids = {}
while beg <= end:
	with open(f'build/scicrunch/{beg}.json') as fp:
		pubs = json.loads(fp.read())
	for pub in pubs:
		if pub['vendor'] == 'MMRRC':
			rrid = pub['rrid']
			if rrid not in rrids: rrids[rrid] = 0
			rrids[pub['rrid']] += 1
			pmid = pub['pmid']
			if pmid not in papers:
				papers[pmid] = {'title': '', 'rrids': []}
			papers[pmid]['title'] = pub['title'] # there may be duplicates
			papers[pmid]['rrids'].append(pub['rrid'])
	beg += delta

##################
# Output Section #
##################

pubmed = 'https://pubmed.ncbi.nlm.nih.gov/'
mmrrc = 'https://www.mmrrc.org/catalog/sds.php?mmrrc_id='

#print('<h1>Publications</h1>')
for pmid in papers:
	print(f'<a href="{pubmed}/{pmid}">{pmid}</a> {papers[pmid]["title"]}', end='')
	txt = []
	for rrid in papers[pmid]['rrids']:
		idx, loc = rrid[11:].split('-')
		txt.append(f' <a href="{mmrrc}{idx}">{rrid[11:]}</a>')
	print(f'{", ".join(txt)}.<br>')

#print('<h1>Products</h1>')
#for rrid, val in sorted(rrids.items(), key=lambda item: item[1], reverse=True):
#	idx, loc = rrid[11:].split('-')
#	print(f'{idx} ({val}) ')


