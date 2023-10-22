import argparse
import json
import os
import requests
import sys
import time

def save_json(filename, data):
	with open(filename, 'w') as fp:
		fp.write(json.dumps(data, indent=4))

def update(arg):
	if not os.path.isdir(arg.data): os.system(f'mkdir {arg.data}')
	url = 'https://api.mmrrc.org/api/v1/catalog/getCatalog'

	for page in (arg.start, arg.end):
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
			print(mid)

#			save_json(f'{arg.data}/{mid}.json', record)

		time.sleep(arg.sleep)

def validate(arg):
	pass
"""
	count = {}
	for n, filename in enumerate(os.listdir(arg.data)):
		#print('processing', filename)
		#if n == 1000: break
		with open(f'{arg.data}/{filename}') as fp:
			data = json.loads(fp.read())
		for key, val in data.items():
			if key not in count: count[key] = 0
			count[key] += 1
			if type(val) == list: # locus only
				for locus in val:
					#print(locus['mmrrc_id'])
					for k2, v2 in locus.items():
						if type(v2) != str:
							raise
						#pass
						#print(k2)
						skey = f'locus:{k2}'
						#print(skey)
						if skey not in count: count[skey] = 0
						count[skey] += 1
	for field in count:
		print(count[field], field, sep='\t')
"""

## CLI top-level ##
parser = argparse.ArgumentParser(description='automated SDS work')
parser.add_argument('data', help='path to data directory')
subparsers = parser.add_subparsers(required=True, help='sub-commands')

### update sub-command
parse_up = subparsers.add_parser('update',
	help='create a new json catalog')
parse_up.add_argument('--start', type=int, default=1, required=False,
	help='starting page number [%(default)i)')
parse_up.add_argument('--end', type=int, default=1000, required=False,
	help='ending page number [%(default)i]')
parse_up.add_argument('--sleep', type=float, default=0.5,
	help='sleep time between API requests [%(default).2f]')
parse_up.set_defaults(func=update)

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

"""
Example record

+ all records have all fields instantiated, even if the value is blank
+ when empty, locus is "" rather than []
+ the locus value may be a

{
    "mmrrc_id": "20426",
    "strain_name": "SIGTR ES cell line AL0418",
    "status": "Accepted",
    "accepted_dt": "2007-03-20",
    "delayed_release_requested": "0",
    "published_name": "",
    "is_transgenic": "",
    "founder_background": "",
    "hom_fertile_comment": "",
    "is_sexlinked": "",
    "genetic_alteration": "",
    "phenotype": "",
    "strain_development": "",
    "availability_level": "",
    "center_id": "UCD",
    "assigned_dt": "2007-03-20",
    "availability": "ES cell line",
    "locus": [
        {
            "mmrrc_id": "20426",
            "alteration": "Gene Trap",
            "alteration_id": "10",
            "additional_notes": "",
            "cell_line_id": "61",
            "symbol": "Bcl2l1",
            "segment_type": "Gene",
            "species": "Mus musculus (mouse)",
            "locus_id": "21967",
            "mgi_acc_id": "MGI:88139",
            "locus_role": "Target",
            "chromosome": "2",
            "name": "BCL2-like 1",
            "external_acc_id": "MGI:88139",
            "resource_id": "MGI",
            "markup_symbol": "Bcl2l1"
        }
    ]
}


"""
