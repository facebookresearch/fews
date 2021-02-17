-------------------------------------------
   Few-shot Examples of Word Sense (FEWS)
-------------------------------------------

This package contains the FEWS (Few-shot Examples of Word Sense) dataset, which consists of WSD examples drawn from Wiktionary and labeled with Wiktionary senses. This dataset was created from the 01/01/2020 "Articles, templates, media/file descriptions, and primary meta-pages" Wiktionary dump. 

This package contains the following files:

fews/
	- README.txt (this file)
	- senses.txt
	- dataset_utils.py
	train/
		- train.txt
		- train.ext.txt
	dev/
		- dev.few-shot.txt
		- dev.zero-shot.txt
	test/
		- test.few-shot.txt
		- test.zero-shot.txt
	raw/
		- quotations.txt
		- examples.txt
		- monosemous.txt

The train/dev/test .txt files consist of a list of line-separated examples in the format (sentence, label), where one or more words in the sentence are marked and correspond the the sense indicated by the label. For example (from the dev set):

	Polonius: What do you read, my lord? / Hamlet: <WSD>Words</WSD>, words, words. \t word.noun.2

The train/dev/test .txt files consist of "quotations" from Wiktionary, that are sentences from news articles, books, and other natural language text sources that contain a specific sense of the word. 

The train.ext.txt file contain the training split of quotations and additionally all of the "illustrations" from Wiktionary, which are text sentences or fragments that use a specific sense of a word and are written by Wiktionary editors (rather than quoted from existing text). These "illustrations" provide additional training data but have significant stylistic differences from the "quotations".

The senses.txt file contains all of the "senses" from Wiktionary. These senses each contain the sense_id, word, gloss (or definition), tags about the sense, the depth of the sense (whether it is a nested sense under a more coarse-grained definition), and any synonyms of the sense contained in Wiktionary; each aspect of the sense is provided on a separate line. An additional blank line is given between each sense. For example, the full sense of the above labeled example, word.noun.2, is:

	sense_id: \t word.noun.2 \n
	word: \t word \n
	gloss: \t The smallest discrete unit of written language with a particular meaning, composed of one or more (letters or symbols and one or more morphemes) \n
	tags: \t noun \n
	depth: \t 2 \n
	synonyms: \n

The dataset_utils.py file contains a set of helper functions to load (and save) these data files into Python objects. The train/dev/test .txt files can be loaded with the load_examples() function. The senses.txt data can be loaded into a sense dictionary with the sense_ids as keys with the load_senses() function. 

The raw/ directory contains the raw data parsed from Wiktionary (quotations and examples) before splitting into train/dev/test splits. The quotations.txt file SHOULD NOT be used to train models, as it contains examples from the test set! However, automatically extracted attributions for each quotation (which are taken from an existing text source) can be found in-line with each quote in the quotations file. This directory also contains the monosemous.txt file, which has all of the examples corresponding to unambiguous words (with only one sense in Wiktionary).

-------------------------------------------
   Citation and Contact
-------------------------------------------

If you use FEWS in your own work, please cite the corresponding paper, "FEWS: Large-scale, Low-shot Word Sense Disambiguation with the Dictionary":

@inproceedings{ 
	blevins2021fews,
	title={FEWS: Large-Scale, Low-Shot Word Sense Disambiguation with the Dictionary},
	author={Terra Blevins and Mandar Joshi and Luke Zettlemoyer},
	booktitle={Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics},
	year={2021},
	url={https://blvns.github.io/papers/eacl2021.pdf}
}


For questions or comments about FEWS, contact Terra Blevins at blvns@cs.washington.edu.