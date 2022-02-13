
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
	if os.path.isfile(f'build/{beg}.json'):
		beg += delta
		continue
	print('downloading', beg)
	os.system(f'wget --no-check-certificate -q "{url}{beg}" -O build/{beg}.json')
	beg += delta
	time.sleep(1)

########################
# Organization Section #
########################

beg = datetime.date(y1, m1, d1)
papers = {}
rrids = {}
while beg <= end:
	with open(f'build/{beg}.json') as fp: pubs = json.loads(fp.read())
	for pub in pubs:
		if pub['vendor'] == 'MMRRC':
			rrids[pub['rrid']] = True
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

for pmid in papers:
	print(f'<a href="{pubmed}/{pmid}">{pmid}</a> {papers[pmid]["title"]}', end='')
	txt = []
	for rrid in papers[pmid]['rrids']:
		idx, loc = rrid[11:].split('-')
		txt.append(f' <a href="{mmrrc}{idx}">{rrid[11:]}</a>')
	print(f'{", ".join(txt)}.<br>')


