ICSC Tools
==========

## pubquarterly.py ##

`pubquarterly.py` is to make quaterly reports on publications

Create directories

	build
	build/scicrunch
	build/pubmed
	build/mmrrc

Run the script. It downloads all the files it needs and creates a report.

	python3 pubquarterly.py 2022-01-01 2022-03-31 > html/2022-Q1.html

## qcsds.py ##

`qcsds.py` downloads all SDS pages and then does some QC activities. There are
several sub-commands. Start by creating the SDS data dump.

	python3 qcsds.py sds update --sleep 0.1

On 2023-10-22, there were 699 pages and 69,891 records (last record 71619).  It
took about 5 hours to run with 0.1 sec between API requests. The tar-ball
weighs in at 723M (73M compressed).
