import argparse
import json
import os
import requests
import sys
import time

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

def count(arg):
	count = {}
	for mid in range(arg.start, arg.end+1):
		jfile = f'{arg.data}/{mid}.json'
		if not os.path.isfile(jfile): continue
		with open(jfile) as fp:
			data = json.loads(fp.read())
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

def validate(arg):
	for mid in range(arg.start, arg.end+1):
		jfile = f'{arg.data}/{mid}.json'
		if not os.path.isfile(jfile): continue
		with open(jfile) as fp:
			data = json.loads(fp.read())

## CLI top-level ##
parser = argparse.ArgumentParser(description='automating SDS stuff')
parser.add_argument('data', help='path to sds data directory')
subparsers = parser.add_subparsers(required=True, help='sub-commands')

### update sub-command
parse_up = subparsers.add_parser('update',
	help='create/update sds.json files')
parse_up.add_argument('--start', type=int, default=1, required=False,
	help='starting page number [%(default)i)')
parse_up.add_argument('--end', type=int, default=100000, required=False,
	help='ending page number [%(default)i]')
parse_up.add_argument('--sleep', type=float, default=0.5,
	help='sleep time between API requests [%(default).2f]')
parse_up.set_defaults(func=update)

### count sub-command
parse_count = subparsers.add_parser('count',
	help='count data in all fields')
parse_count.add_argument('--start', type=int, default=1, required=False,
	help='starting record number [%(default)i)')
parse_count.add_argument('--end', type=int, default=0, required=False,
	help='ending page number [%(default)i]')
parse_count.set_defaults(func=count)

### validate sub-command
parse_val = subparsers.add_parser('validate',
	help='perform some QC checks')
parse_val.add_argument('--start', type=int, default=1, required=False,
	help='starting record number [%(default)i)')
parse_val.add_argument('--end', type=int, default=0, required=False,
	help='ending page number [%(default)i]')
parse_val.set_defaults(func=validate)

### sub-command checkpoint
try:
	arg = parser.parse_args()
except:
	print(f'{sys.argv[0]} requires a sub-command, use --help for more info')
	sys.exit(1)

## Run subcommand ##
arg.func(arg)
