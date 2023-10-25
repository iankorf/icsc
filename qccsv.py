import csv
import sys

with open(sys.argv[1]) as fp:
	reader = csv.reader(fp, delimiter=',', quotechar='"')
	for f in reader:
		print(f[0], f[6], sep='\t')
