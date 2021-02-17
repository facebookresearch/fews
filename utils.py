'''
Copyright (c) Facebook, Inc. and its affiliates.
All rights reserved.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#UTILITIES for dataset creation and data loading

def get_key(label, use_pos):
	if use_pos: key = '.'.join(label.split('.')[:2])
	else: key = label.split('.')[0]
	return key

#load senses into dict from senses.txt file
def load_senses(filepath):
	senses = {}
	with open(filepath, 'r') as f:
		s = {}
		for line in f:
			line = line.strip()
			if len(line) == 0:
				senses[s['sense_id']] = s
				s = {}
			else:
				line = line.strip().split(':\t')
				key = line[0]
				if len(line) > 1: value = line[1]
				else:
					key = key[:-1]
					value = ''
				s[key] = value
	return senses

#load examples (data instances w/o attributions) from txt file
def load_examples(filepath):
	examples = []
	with open(filepath, 'r') as f:
		for line in f:
			sent, label = line.strip().split('\t')
			examples.append((sent, label))
	return examples

#load quotes (data instances w/ attributions) from txt file
def load_quotations(filepath):
	quotations = []
	with open(filepath, 'r') as f:
		for line in f:
			line = line.strip().split('\t')
			sent = line[0]
			label = line[1]
			if len(line) > 2: attrib = line[2]
			else: attrib = ''
			quotations.append((sent, label, attrib))
	return quotations

#save dict of senses to txt file
def save_senses(filepath, senses):
	f = open(filepath, 'w')
	for sense in senses:
		sense_str = 'sense_id:\t'+sense['sense_id']+'\n'
		sense_str += 'word:\t'+sense['word']+'\n'
		sense_str += 'gloss:\t'+ sense['gloss']+'\n'
		sense_str += 'tags:\t'+', '.join(sense['tags'])+'\n'
		sense_str += 'depth:\t'+str(sense['depth'])+'\n'
		sense_str += 'synonyms:\t'+', '.join(sense['synonyms'])+'\n\n'
		f.write(sense_str)
	f.close()
	return

#save list of quotations (with attribution) to txt file
def save_quotations(filepath, quotations):
	f = open(filepath, 'w')
	for quote in quotations:
		attrib = quote[2]
		if type(attrib) == list: attrib = '; '.join(attrib)
		quote_str = quote[0]+'\t'+quote[1]+'\t'+attrib+'\n'
		f.write(quote_str)
	f.close()
	return

#saves list on data examples to txt file
def save_examples(filepath, examples):
	f = open(filepath, 'w')
	for ex in examples:
		ex_str = ex[0]+'\t'+ex[1]+'\n'
		f.write(ex_str)
	f.close()
	return

#EOF