ICSC Tools
==========

pubquarterly.py is to make quaterly reports on publications

## Setup ##

Create directories

	build
	build/scicrunch
	build/pubmed
	build/mmrrc

Run the script. It downloads all the files it needs and creates a report.

	python3 pubquarterly.py 2022-01-01 2022-03-31 > html/2022-Q1.html
