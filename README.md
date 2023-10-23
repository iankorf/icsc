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

On 2023-10-22, there were 699 pages and 69,891 records (last record 71619). It
took about 5 hours to run with 0.1 sec between API requests. The tar-ball
weighs in at 70M compressed (10-fold compression). Because the file isn't so
large, I put it in the repo as `sds.tar.gz`, so unwrap this for a recent
version.

The `count` function examines all of the fields in the SDS.json files to see
how fields are used vs empty. For example, `citation_id` has never been used in
any record, and `esc_please_see_also` has been used 2 times. More troubling,
3760 do not have a creation date and 9897 do not have any reference. The counts
from 2023-10-22 are stored in `count.txt`.

If you add the `--field` option to the `count` function, you can get value
counts for a specific field. It's surprising (or not) how many values are a
single space (rather than being actually empty).

The `explore` function is sort of like `count --field` except that it reports
the mmrrc_ids for each value rather than their count. This might be useful for
manually fixing outliers.

	python3 qcsds.py sds explore current_background --test

I am planning on doing a variety of "fixes". For example, change all of the
values of " " to "". Hopefully, something more useful. These functions will be
called "fix1", "fix2", and the like, and be documented here.
