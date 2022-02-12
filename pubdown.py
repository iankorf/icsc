
import argparse
import datetime
import os
import time

def splitdate(s):
	y, m, d = s.split('-')
	return int(y), int(m), int(d)

parser = argparse.ArgumentParser(description='publications downloader')
parser.add_argument('beg', type=str, metavar='<beg>', help='begin date')
parser.add_argument('end', type=str, metavar='<end>', help='end date')
arg = parser.parse_args()

url = 'https://sci.jonudell.info/public_annos/get_public_annos?day='

y1, m1, d1 = splitdate(arg.beg)
y2, m2, d2 = splitdate(arg.end)

beg = datetime.date(y1, m1, d1)
end = datetime.date(y2, m2, d2)
delta = datetime.timedelta(days=1)

while beg <= end:
	print(beg)
	os.system(f'wget --no-check-certificate -q "{url}{beg}" -O build/{beg}.json')
	beg += delta
	time.sleep(1)

