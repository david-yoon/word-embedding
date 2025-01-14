
## Hanja Graph Project

**Author**: Pablo Estrada \< pablo (at) snu (dot) ac (dot) kr \>
**Author**: David Seunghyun Yoon \< mysmilesh (at) snu (dot) ac (dot) kr \>

This repo contains the code resulting from paper

"Synonym Discovery with Etymology-based Word Embeddings"
<a href="https://ieeexplore.ieee.org/abstract/document/8285290/"> \<link\> </a>


###Folders
* Crawlers - This is the folder containing the crawlers to download the data.
At the moment of this writting, there is just one crawler implemented.
* Formatters - This is the folder containing the small python scripts that take
the files created by the crawlers and output an acceptable graph-format file.
* Analysis - This folder contains the scripts that do analysis over the graph.
* Test_data - This folder contains some data provided for test if anyone would
just want to have the data after all the processing
    * ```graph.graphml``` - This contains the full graph, with links between hanja
    and korean words. No bipartite distinction.
    * ```hanja_list.json``` - This contains the list of hanjas as returned by the
    crawler.
    * ```words.nospace.json``` - This contains the list of korean words, as
    returned by the crawler.
    * ```korean_unip_projection.graphml``` - This file contains the projection of
    the korean words from the bipartite graph. In the current version, the edge
    weights are 1 or 2, depending on how many chinese characters are shared
    between two words.

### Scrapers/Crawlers
#### Scrape Kanjis
These are the utilities to scrape the Kanji information in
'http://www.manythings.org/kanji/d/'. They all serve different purposes.

* `scrape_kanji.py` - This is the main scraper. It gets the data and outputs a JSON file with
  words, and Kanjis. This JSON file can be used to generate the graphml file.
* `make_kanji_graph.py` - This takes the JSON output from `scrape.py`, and makes it into a Graphml
file.

#### Scrape naver
Not yet available : )

### Obtaining synonyms
#### Obtaining the synonyms training set
To generate the synonyms training set we need to follow these steps:

(1) Use the graph dataset to obtain the features of each node pair

`$> nohup ./bin/generate_csv_p.py data/hanja_unip.graphml res.csv 4`

(2) Obtain the 'zeros' in the training set. We do this through random sampling from the main CSV file

`$> shuf -n 1000 data/res.csv > data/training_zeros`

`$> ./bin/removeFirstColumns training_zeros data/training_non_related.csv`

(3) Obtain the 'synonyms' in the training set
    * Obtain a random set of hanjas from the `res.csv` file

`$> shuf -n 1000 data/res.csv | awk -F "," '{print $3}' > data/tmp`

`$> cat data/tmp | sort | uniq > data/random_hanjas.txt`

* Obtain synonyms and antonyms for these hanjas

`$> ./bin/scrapeSynonyms data/random_hanjas.txt data/antonyms_hanja.txt data/synonyms_hanja.txt`

* Get the features from these pairs of synonyms or antonyms

`$> ./bin/extractPairsFromCsv data/synonyms_hanja.txt data/res.csv data/synonyms.csv`

(4). Use the result to run a classification scheme ; )

#### Runing the classification script

(1) Run the classification script

`$> ./bin/get_synonyms.py data/res.csv data/synonyms_training.csv data/training_non_related.csv data/guess_syn1.txt`

(2) Verify the results

`$> ./bin/checkSynonyms data/guess_syn1.txt`

(3) Verify the data by hand // Since Naver does not know all the Hanja synonyms

`$> ./bin/get_pairs_meanings.py data/guess_syn1.txt output [amount]`
