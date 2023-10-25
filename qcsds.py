import argparse
import json
import os
import requests
import sys
import time

def read_all_sds(sdspath, test):
	for path, dirs, files in os.walk(sdspath):
		for i, f in enumerate(files):
			if test and i == 1000: break
			with open(f'{path}/{f}') as fp:
				yield json.loads(fp.read())

def save_json(filename, data):
	with open(filename, 'w') as fp:
		fp.write(json.dumps(data, indent=4))

def get_mids(page):
	url = 'https://api.mmrrc.org/api/v1/catalog/getCatalog'
	call = f'{url}/{page}'
	r = requests.get(call)
	if r.status_code != 200:
		print(f'failure with request {call}', file=sys.stderr)
		raise
	data = json.loads(r.content)
	if len(data) == 0:
		print(f'page limit exceeded at page {page}', file=sys.stderr)
		yield None
	for record in data: yield record['mmrrc_id']

def get_sds(mid):
	url = 'https://api.mmrrc.org/api/v1/catalog/getSDS'
	call = f'{url}/{mid}'
	r = requests.get(call)
	if r.status_code != 200:
		print(f'failure with request {call}', file=sys.stderr)
		raise
	return json.loads(r.content)

def update(arg):
	if not os.path.isdir(arg.data): os.system(f'mkdir {arg.data}')
	for page in range(arg.start, arg.end+1):
		print(f'processing page {page}', file=sys.stderr)
		for mid in get_mids(page):
			if mid is None: sys.exit(0)
			print(f'{mid}', end=' ', file=sys.stderr)
			data = get_sds(mid)
			save_json(f'{arg.data}/{mid}.json', data)
			time.sleep(arg.sleep)
		print(file=sys.stderr)
		time.sleep(arg.sleep)

def count_field(arg):
	count = {}
	for data in read_all_sds(arg.data, arg.test):
		val = data[arg.field]
		if val not in count: count[val] = 0
		count[val] += 1
	for key, val in sorted(count.items(), key=lambda item: item[1]):
		print(val, f"'{key}'", sep='\t')
	sys.exit(0)

def count(arg):
	if arg.field: count_field(arg)
	count = {}
	for data in read_all_sds(arg.data, arg.test):
		for key, val in data.items():
			if key not in count and key != 'alterations':
				count[key] = {'null': 0, 'str': 0}
			if type(val) == str:
				if val == '': count[key]['null'] += 1
				else:         count[key]['str'] += 1
			elif type(val) == list: # only for alterations
				for alt in val:
					for k2, v2 in alt.items():
						skey = f'{key}.{k2}'
						if skey not in count:
							count[skey] = {'null': 0, 'str': 0}
						if type(v2) == str:
							if val == '': count[skey]['null'] += 1
							else:         count[skey]['str'] += 1
						else:
							print('unexpected non-str value')
							sys.exit(1)
			else:
				print('unexpected type', type(val))


	for f in count:
		print(f, count[f]['str'], count[f]['null'], sep='\t')

def explore(arg):
	count = {}
	for data in read_all_sds(arg.data, arg.test):
		val = data[arg.field]
		if val not in count: count[val] = []
		count[val].append(data['mmrrc_id'])
	for key, val in sorted(count.items(), key=lambda item: len(item[1]),
			reverse=True):
		print(f"'{key}' {len(val)}")
		for mid in val:
			print(f'\t{mid}')

def find(arg):
	for data in read_all_sds(arg.data, arg.test):
		found = True
		for query in arg.query:
			tag, val = query.split(':')
			if data[tag] != val:
				found = False
				break
		if found: print(data['mmrrc_id'])

def validate(arg):
	for data in read_all_sds(arg.data, arg.test):
		if data['sds_status'] == 'N/A': print(data['mmrrc_id'])

def fix1(arg):
	pass

def fix2(arg):
	pass

def custom1(arg):
	avail = {}
	with open('availability.tsv') as fp:
		for line in fp:
			f = line.split()
			if   len(f) == 1: avail[f[0]] = '?'
			elif len(f) == 2: avail[f[0]] = f[1]
			else: avail[f[0]] = ' '.join(f[1:])
	
	print('mmrrc_id', 'availability', 'sds_status', 'public_display', sep=',')
	for data in read_all_sds(arg.data, arg.test):
		mid = data['mmrrc_id']
		if mid not in avail: avail[mid] = 'missing'
		print(avail[mid], data['sds_status'], data['public_display'])

# CLI top-level
parser = argparse.ArgumentParser(description='automating SDS stuff')
parser.add_argument('data', help='path to sds data directory')
subparsers = parser.add_subparsers(required=True, help='sub-commands')

# update sub-command
parse_up = subparsers.add_parser('update',
	help='create/update sds.json files')
parse_up.add_argument('--start', type=int, default=1, required=False,
	help='starting page number [%(default)i)')
parse_up.add_argument('--end', type=int, default=100000, required=False,
	help='ending page number [%(default)i]')
parse_up.add_argument('--sleep', type=float, default=0.5,
	help='sleep time between API requests [%(default).2f]')
parse_up.set_defaults(func=update)

# count sub-command
parse_count = subparsers.add_parser('count',
	help='count data in all fields')
parse_count.add_argument('--field', type=str, required=False,
	help='examine a specific field')
parse_count.add_argument('--test', action='store_true')
parse_count.set_defaults(func=count)

# explore sub-command
parse_explore = subparsers.add_parser('explore', help='deep dive on field')
parse_explore.add_argument('field')
parse_explore.add_argument('--test', action='store_true')
parse_explore.set_defaults(func=explore)

# find sub-command
parse_find = subparsers.add_parser('find',
	help='find records as tag:value with implicit AND between queries')
parse_find.add_argument('query', nargs='*', help='tag:value')
parse_find.add_argument('--test', action='store_true')
parse_find.set_defaults(func=find)

# validate sub-command
parse_val = subparsers.add_parser('validate', help='perform some QC checks')
parse_val.add_argument('--test', action='store_true')
parse_val.set_defaults(func=validate)

# fix sub-commands (planning for several)
parse_fix1 = subparsers.add_parser('fix1', help='repair #1')
parse_fix1.add_argument('--test', action='store_true')
parse_fix1.set_defaults(func=fix1)

parse_fix2 = subparsers.add_parser('fix2', help='repair #2')
parse_fix2.add_argument('--test', action='store_true')
parse_fix2.set_defaults(func=fix2)

# custom scripts
parse_c1 = subparsers.add_parser('custom1', help='reese request 1')
parse_c1.add_argument('--test', action='store_true')
parse_c1.set_defaults(func=custom1)

# sub-command checkpoint
try:
	arg = parser.parse_args()
except:
	print(f'{sys.argv[0]} requires a sub-command, use --help for more info')
	sys.exit(1)

# Run subcommand
arg.func(arg)
sys.exit(0)
