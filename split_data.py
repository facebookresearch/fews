'''
Copyright (c) Facebook, Inc. and its affiliates.
All rights reserved.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import random
#set random seed to data splitting will be deterministic 
#(assuming same wiktionary dump files)
random.seed(42)

from utils import *

parser = argparse.ArgumentParser(description='Split Low-Shot WSD data into train/dev/test')
parser.add_argument('--raw-dir', type=str, required=True,
	help='Filepath to the extracted Wiktionary data')
parser.add_argument('--save-dir', type=str, required=True,
	help='Filepath at which to save split data')

#sizes of zero shot and few shot eval data
#(later split between dev and test)
ZERO_SIZE = 10000
FEW_SIZE = 10000


USE_POS = True

def clean_eval_sent(sent):
	ex_idx = sent.find('</WSD>')+6 #point to end of first example
	sent = sent[:ex_idx]+sent[ex_idx:].replace('<WSD>', '').replace('</WSD>', '')
	return sent
	
#splits data into/train/dev/test
def split_data(data, senses):
	#size of dataset before splitting
	print(len(data))

	#filter out these words from dev/test sets
	ignored_tags = set(['obsolete', 'rare', 'archaic', 'dated', 'nonstandard', 'vulgar']) #historical?

	random.shuffle(data)

	#get label support for data
	label_support = {}
	for _, l, _ in data:
		if l in label_support:
			label_support[l] += 1
		else:
			label_support[l] = 1
	
	train_split = []
	zero_split = []
	few_split = []
	test_labels = set()
	for sent, label, attrib in data:
		#check for ignored tags in that word's sense
		sense = senses[label]
		if ', ' in sense['tags']: sense_tags = ', '.split(sense['tags'])
		else: sense_tags = [sense['tags']]
		
		#if not ignored tags...
		key = get_key(label, use_pos=USE_POS)
		if set(sense_tags).isdisjoint(ignored_tags) and label not in test_labels:
			#put into zero shot or few shot test sets if not full
			#note: only including polysemous words (word+pos) in eval sets
			if label_support[label] == 1 and len(zero_split) < ZERO_SIZE:
				sent = clean_eval_sent(sent) #so there is only one labeled example per eval sent
				zero_split.append((sent, label, attrib))
				test_labels.add(label)
			elif label_support[label] > 1 and len(few_split) < FEW_SIZE:
				sent = clean_eval_sent(sent) #so there is only one labeled example per eval sent
				few_split.append((sent, label, attrib))
				test_labels.add(label)
			else:
				train_split.append((sent, label, attrib))
		else:
			train_split.append((sent, label, attrib))
	
	#split fewshot and zero-shot examples between dev and test
	fs_dev_split = few_split[:FEW_SIZE//2]
	zs_dev_split = zero_split[:ZERO_SIZE//2]
	fs_test_split = few_split[FEW_SIZE//2:]
	zs_test_split = zero_split[ZERO_SIZE//2:]

	#size of dataset after splitting
	print(len(train_split), len(fs_dev_split), len(zs_dev_split), len(fs_test_split), len(zs_test_split))
	return train_split, fs_dev_split, zs_dev_split, fs_test_split, zs_test_split

def filter_monosemous_data(data, senses):
	#build sense inventory
	sense_inv = {}
	for label in senses:
		key = get_key(label, use_pos=USE_POS)
		if key in sense_inv: sense_inv[key] += 1
		else: sense_inv[key] = 1

	#filter out monosemous examples (examples with one sense)
	polysemous = []
	monosemous = []
	for d in data:
		key = get_key(d[1], use_pos=USE_POS)
		if sense_inv[key] > 1:
			polysemous.append(d)
		else:
			monosemous.append(d)

	return polysemous, monosemous

def filter_senses(data, filters):
	print(filters[0])
	filters = set([l for _, l, _ in filters])

	filtered_data = []
	for example, label in data:
		if label not in filters:
			filtered_data.append((example, label))

	return filtered_data

def main(args):
	#load parsed wiktionary data
	q_path = os.path.join(args.raw_dir, 'quotations.txt')
	quotes = load_quotations(q_path)
	s_path = os.path.join(args.raw_dir, 'senses.txt')
	senses = load_senses(s_path)
	ex_path = os.path.join(args.raw_dir, 'examples.txt')
	examples = load_examples(ex_path)

	#split quotes into train/dev/test
	data, monosemous_data = filter_monosemous_data(quotes, senses)
	train, fs_dev, zs_dev, fs_test, zs_test = split_data(data, senses)

	#save train data
	train_path = os.path.join(args.save_dir, 'train.txt')
	save_examples(train_path, train)

	#create and save train extended 
	#(adds examples as extra train data)
	random.shuffle(examples)
	#filter monosymous senses from examples
	ext, monosemous_ext = filter_monosemous_data(examples, senses)
	#filter senses in zero-shot splits from examples
	zero_shot_examples = zs_dev+zs_test
	ext = filter_senses(ext, zero_shot_examples) 
	ext = train+ext
	ext_path = os.path.join(args.save_dir, 'train.ext.txt')
	save_examples(ext_path, ext)

	#save dev data
	fs_dev_path = os.path.join(args.save_dir, 'dev.few-shot.txt')
	save_examples(fs_dev_path, fs_dev)
	zs_dev_path = os.path.join(args.save_dir, 'dev.zero-shot.txt')
	save_examples(zs_dev_path, zs_dev)

	#save test data
	fs_test_path = os.path.join(args.save_dir, 'test.few-shot.txt')
	save_examples(fs_test_path, fs_test)
	zs_test_path = os.path.join(args.save_dir, 'test.zero-shot.txt')
	save_examples(zs_test_path, zs_test)

	#save monosemous examples as extra data
	mono_path = os.path.join(args.save_dir, 'monosemous.txt')
	mono_examples = monosemous_data+monosemous_ext
	save_examples(mono_path, mono_examples)

if __name__ == "__main__":
	args = parser.parse_args()
	main(args)

#EOF