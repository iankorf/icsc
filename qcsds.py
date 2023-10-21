import argparse
import json
import os
import requests
import sys
import time

def save_json(filename, data):
	with open(filename, 'w') as fp:
		fp.write(json.dumps(data, indent=4))

def create(arg):
	if not os.path.isdir(arg.data): os.system(f'mkdir {arg.data}')
	url = 'https://api.mmrrc.org/api/v1/catalog/getCatalog'
	
	page = 1
	while True: 
		call = f'{url}/{page}'
		r = requests.get(call)
		if r.status_code != 200:
			print(f'failure with request {call}', file=sys.stderr)
			raise
		data = json.loads(r.content)
		if len(data) == 0:
			print(f'page limit exceeded at page {page}', file=sys.stderr)
			break
		print(f'processing page {page}', file=sys.stderr)
		for record in data:
			mid = record['mmrrc_id']
			save_json(f'{arg.data}/{mid}.json', record)
		
		page += 1
		time.sleep(arg.sleep)

def validate(arg):
	pass

## CLI top-level ##
parser = argparse.ArgumentParser(description='automated SDS work')
parser.add_argument('data', help='path to data directory')
subparsers = parser.add_subparsers(required=True, help='sub-commands')

### create sub-command
parse_create = subparsers.add_parser('create',
	help='create a new json catalog')
parse_create.add_argument('--sleep', type=float, default=0.5,
	help='sleep time between API requests [%(default).2f]')
parse_create.set_defaults(func=create)

### validate sub-command
parse_validate = subparsers.add_parser('validate',
	help='check for errors')
parse_validate.set_defaults(func=validate)

### sub-command checkpoint
try:
	arg = parser.parse_args()
except:
	print(f'{sys.argv[0]} requires a sub-command, use --help for more info')
	sys.exit(1)

## Run subcommand ##
arg.func(arg)
