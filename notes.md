QC Notes
========

There are a lot of inconsistencies in our data.

## Schema ##

The submission schema is advertised, but what about the other schemata like
SDS?

### Boolean values

+ Why do we enumerate Boolean as "Yes"/"No" and "1"/"0" but not true/false?
+ Why is there more than one Boolean representation?
+ If Yes/No is Boolean, why do Yes/No appear in non-boolean contexts?
+ Why does homozygosity_yn exist rather than is_homozygous?

### String values

+ Why is everything a string, even integer values?
+ Why are empty arrays represented as empty strings rather than empty arrays?

### Alterations

+ Why are "genetic_alterations" in SDS called "locus" in catalog?
+ Why is one plural and the other singular?
+ how do any of the alterations get defined?
	+ where does "is_standard" come from?
	+ where does "subtype_of" come from and why a numeric value?

### Other

+ Why is there a species enum? Do we take non-mice?
+ Why are the species names non-standard?
+ Why not use NCBI taxid?


## SDS JSON ##

The SDS pages are a bit of a mess. Let's take a look at a few areas that could
use improvement.


### breeding_system

This name is required in the schema and is defined as an enum.

```
	"required": [
		"published_name",
		"is_transgenic",
		"is_sexlinked",
		"genetic_alteration",
		"phenotype",
		"reference",
		"strain_development",
		"current_background",
		"available_control",
		"coat_color",
		"breeding_system",  <-------------- here
		"hide_colony_husbandry_info",
		"show_repro_stat",
		"sds_status",
		"protocol_status",
		"public_display"
	]

	"breeding_system": {
		"enum": [
			"Backcross",
			"Sib-mating",
			"Random intra-strain mating",
			"Outcross to non inbred (hybrid or outbred) mate",
			"Other or uncertain",
			"Backcross or Sib-Mating"
		]
	}
```

All strains should have breeding_system in one of the enum values. Instead,
there are lots of empty records and free text.

+ '' 40282 - how can there be so many blank records? this is _required_
+ "Backcross" 687
	+ '<p>Backcross</p>' 4
	+ 'Backcross<br>' 3
+ "Sib-mating" 591
	+ 'Sib mating' 58
	+ 'Inbred sib-mating' 7
	+ 'Intrastrain' 7
	+ 'Sib Mating' 3
+ "Random intra-strain mating" 5206
	+ 'Intra-strain Random Mating' 328
	+ 'Intra-strain' 159
	+ 'Intra-strain random mating' 14
	+ 'Inbred' 10
+ "Outcross to non inbred (hybrid or outbred) mate"
+ "Other or uncertain" 353
	+ 'Backcross, Sib-mating or Outcross to Crl:CD1(ICR)' 741
	+ 'Backcross, Sib-matting or Outcross to Swiss Webster' 383
	+ 'Outcross to non-inbred (hybrid or outbred) mate' 37
	+ 'Backcross, Sib-mating or Outcross to IcrTac:ICR' 35
	+ 'Outcross to Crl:CD1(ICR)' 11
	+ 'Selective Breeding' 7
	+ 'Selective breeding' 5
+ Backcross or Sib-Mating" 19254
	+ 'Backcross or Sib-mating' 943
	+ 'Backcross and sib-mating' 156
	+ 'Backcross or Inbreeding' 126
	+ 'Backcross or Sib-mated' 25
	+ 'Backcross and random intra-strain mating' 27
	+ 'Backcross and sib-mating<br>' 24
	+ 'Backcross then sib-mating' 22
	+ 'Backcross or Random intra-strain mating' 14
	+ 'Sib mating or Backcross' 8
	+ 'Backcross or Sib mating' 7
	+ 'Backross and sib-mating' 6
	+ 'Backcrossing and random intra-strain mating' 5
	+ 'Backcrossand sib-mating<br>' 4
	+ 'Sib-mating or Backcross' 4
	+ 'Backcross or Intra-strain Random Mating' 4
	+ 'Backcrossing and sib-mating' 3
	+ '<p>Backcross and sib-mating</p>' 3

### coat_color

Given all the variations on a theme, why isn't coat_color an enum? Even if it
was an enum, would it be enforced? Why are so many blank?

+ '' 38164
+ 'Black' 8164
+ 'black' 3997
+ 'BLACK' 22
+ '<p>Black</p>' 3
+ '1' 4
+ 'N/A' 4

### eye_color

There isn't in the submission schema. How does it get populated? If so many are
blank, why do we even use it? Is Agouti an eye color?

+ '' 68744
+ 'Black' 885
+ 'black' 60
+ 'Agouti' 1

### research_applications

Why do we store lists as html rather than actual lists? How do we search on
individual elements? Why do we have so many blank values?

+ '' 65148
+ '<li>Cell Biology
            </li>
      <li>Developmental Biology
            </li>
      <li>Neurobiology
            </li>
      <li>Research Tools</li>' 678


## General Problems ##

+ There are 69886 records
+ Many properties are empty: ""

```
    property                empty
    --------                -----
	doc_title               66397
	published_name          30948
	genetic_alteration      32767
	genotyping              51107
	es_cell_line            67004
	phenotype               52295
	founder_background      65195
	current_background      37117
	research_applications   65143
	addl_reference          69824 <--- used 62 times
	coat_color              38163
	eye_color               68741	
	breeding_system         40281
	citation_id             69886 <-- never used
	etc
```

### doc_title

95% of records do not have a doc_title. What is the point of storing a useless
HTML tag inside the database when it can be generated from the mmrrc_id?

There are duplicate titles. Some different strains share the same title.

+ 31781: 31781 32781
+ 31782: 31782 32782
+ 31778: 31778 32778
+ 31779: 31779 32779

### published_name

Appears to be a comma separated list, sometimes with genotype. Some of the
lists have trailing commas. Some names don't look like published names. Why
isn't this an actual list?

There are a bunch of test pages you can get from API but not website.

+ 'Best Strain Ever, BSE' 37127 37084
+ '., .' 37630 36970 36971
+ 'MY Test Strain, Test Strain' 37060 37083
+ 'test, test' 37364 37363 37056
+ '1, 1' 36824 36817 36816 36747

### founder_background & current_background

It's understandable that founder_background could be free text, but shouldn't
the current_background come from an enum?


### es_cell_line

Lots of records have pseudo-empty values containing a single space. This
happens in almost every field of the JSON. Almost every property has many
records with these one-space values. There are also a lot of accidental
embedded HTML tags.

+ '' 67007
+ ' ' 1400
+ 'Not applicable' 366
+ 'JM8A3.N1 derived from C57BL/6N' 85
+ 'JM8A3.N1 derived from C57BL/6N<br>' 2
+ 'JM8A3 derived from C57BL/6N' 60
+ 'Not applicable<div><br></div>' 3
+ '<p><i>Sag<sup>tm1Jnc</sup></i> allele: unspecified ESCs derived from 129S4/SvEvBrd </p>' 3


### markup_symbol

There are lots of ways to craft the HTML so that it _looks_ correct. What is
the proper way to mark these up? Some kind of XML that gets converted to style,
I think. Not this mish-mash of sometimes unbalanced tags.

```
	8029 <i> </i> <sup> <i> </i> </sup>
	2369 <i> <sup> </sup> </i>
	979 <i> </i> <sup> <i> </i> </sup> <i> </i> <sup> <i> </i> </sup>
	  5 <em> <sup> </sup> </em>
	  4 <i> <sup> </i> </sup>
	  1 <i> </i> <sup> <i> </i> </sup> <i> <sup> </i> </sup>
	  1 <i> </i> <sup> <i> </sup> </i> <sup> <i> </i> </sup>
	  1 <i> <sup> </sup> <sup> </sup> </i>
	  1 <I> <sup> </sup> </i>
```