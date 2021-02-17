'''
Copyright (c) Facebook, Inc. and its affiliates.
All rights reserved.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
import os
import time
from difflib import SequenceMatcher

from utils import *

'''
This script takes in a Wiktionary dump file and parses it into 
a fow-shot WSD dataset.
'''

parser = argparse.ArgumentParser(description='FEWS Dataset Creation Script')
parser.add_argument('--wiki-file', type=str, required=True,
	help='Filepath to the Wiktionary dump file to be parsed')
parser.add_argument('--save-dir', type=str, required=True,
	help='Filepath at which to save parsed Wikitionary pages')

#parts-of-speech we track for senses 
PARTS_OF_SPEECH = ['noun', 'verb', 'adjective', 'adverb', 'proper noun']

CHAR_THRESHOLD = 9 #examples should contain 15+ chars
MIN_MENTION_RATIO = 0.5 #mention of sense overlaps this % with base sense form

#calculates longest common subsequence between two strings
def lcs(str1, str2):
	s = SequenceMatcher(None, str1, str2)
	m = s.find_longest_match(0, len(str1), 0, len(str2))
	if m.size > 0:
		return str1[m.a: m.a+m.size]
	else:
		return ''

#cleans text from wikipedia to get rid of meta data, wiki markup, html formatting
def clean_text(text, match_sense=''):
	#get rid of meta data
	text = re.sub(r'\[\[Category:.*?\]\]', '', text)
	text = re.sub(r'\[\[File:.*?\]\]', '', text)
	text = re.sub(r'/ :*? \'\'\'Usage.*$', '', text)


	#fix math+ symbols
	text = re.sub(r'&lt;', '<', text)
	text = re.sub(r'&gt;', '>', text)
	text = re.sub(r'&amp;', '&', text)
	text = re.sub(r'&nbsp;|&emsp;', ' ', text)
	text = re.sub(r'&hellip;', '...', text)
	text = re.sub(r'<math>|</math>|<sup>|</sup>', '', text)
	text = re.sub(r'\\forall', '∀', text)
	text = re.sub(r'\\exists', '∃', text)
	text = re.sub(r'\\pi', 'π', text)
	text = re.sub(r'\\dot', '·', text)
	text = re.sub(r'<br/?>', '/ ', text)

	#parse these metadata links out
	matches = re.finditer(r'{{.*?}}', text)
	for m in matches:
		value = m.group(0)
		value = re.sub(r'{{|}}', '', value)
		value = '('+value.strip().split('|')[-1]+')'
		text = re.sub(r'{{.*?}}', value, text, count=1)

	#parse out links
	matches = re.finditer(r'\[\[.*?\]\]', text)
	for m in matches:
		value = m.group(0)
		value = re.sub(r'\[\[|\]\]', '', value)
		value = ''+value.strip().split('|')[-1]+''
		if value == '\\': value = '\\\\'
		text = re.sub(r'\[\[.*?\]\]', value, text, count=1)
	text = re.sub(r'\[\[|\]\]', '', text)


	text = re.sub(r'{{|}}', '', text)

	if match_sense != '':
		word = match_sense.split('.')[0].replace('_', ' ')
		matches = re.finditer(r'\'\'\'.*?\'\'\'', text)
		for m in matches:
			value = m.group(0)
			value = re.sub(r'\'\'\'', '', value)
			if len(value) > 0 and len(lcs(value.lower(), word))/len(value) > MIN_MENTION_RATIO: 
				text = re.sub(r'\'\'\'.*?\'\'\'', '<WSD>'+value+'</WSD>', text, count=1)
			else:
				text = re.sub(r'\'\'\'.*?\'\'\'', value, text, count=1)

	#fix quotation marks
	text = re.sub(r'’', '\'', text)
	text = re.sub(r'&quot;', '"', text)
	text = re.sub(r'(?<!\')\'{2}(?!\')', '"', text)
	text = re.sub(r'&ldquo;|&rdquo;', '"', text)

	#cleaning whitespace in text
	text = ' '.join([t.strip() for t in text.split(' ')])

	text = text.strip()
	if match_sense != '':
		context = re.sub(r'<WSD>.*?</WSD>', '', text)
		if '<WSD>' in text and ' ' in context:
			return text
		else:
			return ''
	else:
		return text

#creates a new sense object for the given word and pos
def generate_sense(word, pos):
	s = {'word':word,
		'gloss':'', 
		'pos': pos,
		'tags':[],
		'examples':[],
		'quotations':[],
		'synonyms':[],
		'depth':-1}
	return s

#processes the gloss contained in given line
def process_gloss(line):
	depth = len(line)-len(line.lstrip('#')) #to get number of # at beginning of line
	line = line.strip('#').strip()

	#strip out tags, comments
	gloss = re.sub(r'{{lb.*?}}', '', line).strip()
	gloss = re.sub(r'&lt;!--.*?--&gt;', '', gloss).strip()
	gloss = clean_text(gloss)

	#ignore senses with no gloss or only tags in gloss (not text)
	if len(gloss) == 0 or len(re.sub(r'\(.*?\)\.?', '', gloss.strip())) == 0: 
		return -1, -1, -1 
	
	#parse tags
	tags = []
	t = re.search(r'{{lb(.*?)}}', line)
	if t: 
		tags = t.group(1).strip().split('|')[1:]

	return gloss, depth, tags

#processes the example text contained in given line
def process_example(line):
	ex = re.sub(r'#*?: {{ux', '', line)
	ex = re.sub(r'}}', '', ex).strip().split('|')[-1]

	if len(ex) > CHAR_THRESHOLD and ' ' in ex:
		return ex
	else:
		return -1

#processes the synonyms in a given line
def process_synonym(line):
	syn = re.sub(r'#*?: {{syn', '', line)
	syn = re.sub(r'}}', '', syn).split('|')[1:]
	if syn[0] == 'en': syn = syn[1:]
	syn = [s for s in syn if 'Thesaurus:' not in s]

	return syn

#process the quotation (and attribution) in a given line
def process_quotation(line):
	quote_flags = ('passage=', 'text=')
	line = re.sub(r'#*?\*:?', '', line)

	if 'seemorecites' in line.lower():
		return -1, -1

	if '|| QUOTE=' in line:
		q = line.split('|| QUOTE=')
		q_tags = q[0]
		if len(q) > 2: q = '/ '.join(q[1:])
		else: q = q[1]

		if re.search(r'{{.*?}}', q):
			q = re.sub(r'{{|}}', '', q)
			q = q.split('|')[-1]
			q = re.sub(r'passage=|text=', '', q)

	elif re.search(r'&lt;ref&gt;.*?&lt;/ref&gt;', line):
		q_tags = re.search(r'&lt;ref&gt;(.*?)&lt;/ref&gt;', line).group(1)
		q = re.sub(r'&lt;ref&gt;.*?&lt;/ref&gt;', '', line)

	elif re.search(r'{{.*?}}', line):
		q_tags = re.sub(r'{{|}}', '', line)
		q_tags = [t.strip() for t in q_tags.strip().split('|')]
	
		q = [t for t in q_tags if t.lower().startswith(quote_flags)]
		if len(q) > 0:
			q = re.sub(r'passage=|text=', '', q[0])
			q_tags = [t for t in q_tags if not t.lower().startswith(quote_flags)]

		else:
			q = [t for t in q_tags if not re.match(r'^.*?=', t)]
			if len(q) > 0: #hopefully this is okay
				q = q[-1]
				q_tags = [t for t in q_tags if t != q]
			else:
				return -1, -1

	#assuming the quote is here in quotes
	else: 
		#cleaning double quotes to parse examples
		line = re.sub(r'(?<!\')\'{2}(?!\')', '"', line)
		if re.search(r'".*?"', line):
			q = re.search(r'".*?"', line)
			q = q.group(0)
			q = re.sub(r'"', '', q)
			q_tags = re.sub(r'".*?"', '', line)
		else:
			q = line
			q_tags = []

	if len(q) > CHAR_THRESHOLD and ' ' in q:
		return q, q_tags
	else:
		return -1, -1

#compresses split line that contain shared (quotation) information
def compress_lines(lines):
	compressed = []
	for line in lines:
		if line.startswith('#'):
			#for second+ line of a quotation
			if re.match(r'#*?\*:', line):
				if len(compressed) > 0:
					l = re.sub(r'#*?\*:', '', line)
					l = l.strip()
					l = compressed[-1]+' || QUOTE='+l
					compressed[-1] = l 
				else:
					continue
			else: 
				compressed.append(line)
		else: #attach to prev line with #
			if len(compressed) > 0: compressed[-1] = compressed[-1]+line
	return compressed

#processes lines of a given sense into sense object
#also gets examples, quotations with that sense and store in obj
def process_sense(lines, word, pos):
	sense = generate_sense(word, pos)
	
	#process first line in sense as definition/gloss
	line = lines[0]
	gloss, depth, tags = process_gloss(line)
	if gloss == -1: return -1
	sense['gloss'] = gloss
	sense['depth'] = depth
	sense['tags'].extend(tags)

	#clean up lines formatting
	lines = compress_lines(lines[1:])

	#rest of lines are quotes, examples, or synonyms
	if len(lines) > 0:
		for line in lines:
			#example text
			if re.match(r'#*?: {{ux', line):
				ex = process_example(line)
				if ex != -1:
					sense['examples'].append(ex)

			#synonyms
			elif re.match(r'#*?: {{syn', line):
				syn = process_synonym(line)
				sense['synonyms'].extend(syn)

			#quotes
			elif re.match(r'#*?\* ', line):
				q, q_tags = process_quotation(line)
				if q != -1:
					quote = (q, q_tags)
					sense['quotations'].append(quote)

	return sense

#processes senses of a given pos for the given word
def process_pos(lines, word, pos):
	senses = []
	#track current POS and get glosses with their appropriate pos, domain if applicable
	in_sense = False
	sense_lines = []
	for line in lines:
		#this starts a sense, with gloss and tags
		if re.match(r'^#* ', line): 
			if in_sense:
				if len(sense_lines) > 0: 
					sense = process_sense(sense_lines, word, pos)
					if sense != -1: 
						senses.append(sense)
			sense_lines = [line]
			in_sense = True
		elif in_sense:
			sense_lines.append(line)
	#process last sense
	if len(sense_lines) > 0:
		sense = process_sense(sense_lines, word, pos)
		if sense != -1: senses.append(sense)

	return senses

#processes the senses in a language (EN) for a given word
def process_language(word, lines):
	senses = []
	pos = ''
	pos_lines = []

	for line in lines:
		if line.startswith('='):
			if line.strip('=').lower() in PARTS_OF_SPEECH: 
				if pos in PARTS_OF_SPEECH:
					#clean up
					s = process_pos(pos_lines, word, pos)
					senses.extend(s)
					pos_lines = []
				pos = line.strip('=').lower()
			elif pos in PARTS_OF_SPEECH:
				s = process_pos(pos_lines, word, pos)
				senses.extend(s)
				pos_lines = []
				pos = ''
		
		elif pos != '':
			pos_lines.append(line)

	#clean up last pos if not done
	if len(pos_lines) > 0:
		s = process_pos(pos_lines, word, pos)
		senses.extend(s)

	if len(senses) > 0:
		return senses
	else:
		return -1

#processes a wiktionary page for a specific word into a list of senses of that word
def process_page(lines):
	senses = []

	#get title/word for page
	title = [line.replace('<title>', '').replace('</title>', '') for line in lines if line.startswith('<title>')][0]
	#ignoring structural, management pages
	if re.match(r'^\w*?:', title): return -1 #ignore these pages
	else: word = title

	#remove html from text to process clean page
	l = []
	for line in lines:
		line = re.sub('<.*?>.*?</.*?>', '', line)
		line = re.sub('<.*?>', '', line)
		line = line.strip()
		if len(line) != 0: l.append(line)
	if len(l) == 0: return -1 #ignore pages with no text outside of html code
	else: lines = l

	#check if there are languages, and process each language seperately 
	langs_count = len([1 for line in lines if re.match(r'^==[^=]*?==$', line)])

	if langs_count > 0:
		in_lang = False
		lang_lines = []
		lang = ''
		for line in lines:
			if re.match(r'^==[^=]*?==$', line):
				lang = line.replace('==', '')
				lang_lines = []
				if lang == 'English': in_lang = True
				else: in_lang = False 
			elif in_lang:
				if line == '----':
					l = process_language(title, lang_lines)
					if l != -1: 
						senses.extend(l)
					in_lang = False
					lang_lines = []
				else:
					lang_lines.append(line)
		#process last language 
		if in_lang:
			l = process_language(title, lang_lines)
			if l != -1: 
				senses.extend(l)
	#otherwise assumed to be only English and processed as one language
	else:
		l = process_language(title, lines)
		if l != -1: 
			senses.extend(l)

	if len(senses) > 0:
		return senses
	else:
		return -1

#generate a word key (word+pos) for given sense
def generate_word_key(sense):
	if sense['pos'] == 'proper noun':
		return '{}.{}'.format(sense['word'].lower().replace(' ','_'), 'noun')
	else:
		return '{}.{}'.format(sense['word'].lower().replace(' ','_'), sense['pos']) 

#pulls out quotes and examples from sense objects and 
#creates a list of each to save seperately
def post_processing(senses):
	quotes = []
	examples = []

	#for each word, pos pair, generate idxs
	word_keys = set([generate_word_key(s) for s in senses])
	word_idxs = {}
	for w in word_keys:
		word_idxs[w] = 0

	#pull out examples, quotations
	for s in senses:
		#generate sense id
		word_k = generate_word_key(s)
		s_id = '{}.{}'.format(word_k, word_idxs[word_k])
		word_idxs[word_k] += 1

		#label with sense_id
		s['sense_id'] = s_id
		#pull out any quotes
		if len(s['quotations']) > 0:
			for x, attrib in s['quotations']:
				sent = clean_text(x, match_sense=s_id)
				if len(sent) > 0:
					q = (sent, s_id, attrib)
					quotes.append(q)

		#pull out any examples
		if len(s['examples']) > 0:
			for x in s['examples']:
				sent = clean_text(x, match_sense=s_id)
				if len(sent) > 0:
					e = (sent, s_id)
					examples.append(e) 
		#remove quotes, examples lists from sense obj
		s.pop('quotations')
		s.pop('examples')

	return senses, quotes, examples

#processes a given wiktionary dump file into a list of senses
#and lists of quotations and examples with sense-disambiguated examples.
def main(args):
	#load wikitionary dump data file
	start_time = time.time()
	f = open(args.wiki_file, 'r')

	#track status in file
	curr_page = []
	is_page = False

	#track all info for dataset
	senses = []

	#scan through file and process pages sequentially 
	for line in f:
		line = line.strip()
		if line == '<page>': 
			is_page = True
		elif line == '</page>': 
			s = process_page(curr_page)
			if s != -1: senses.extend(s)
			is_page = False
			curr_page = []
		else:
			#drop empty lines
			if is_page and len(line)>0: curr_page.append(line)
	f.close()
	print(len(senses), '{:.2f}'.format(time.time()-start_time))

	#add post-processing to seperate out quotes, examples into seperate lists
	senses, quotations, examples = post_processing(senses)

	#make save dir if it doesn't exist
	if not os.path.exists(args.save_dir):
		os.makedirs(args.save_dir)

	#save senses
	s_path = os.path.join(args.save_dir, 'senses.txt')
	save_senses(s_path, senses)

	#save examples
	e_path = os.path.join(args.save_dir, 'examples.txt')
	save_examples(e_path, examples)

	#save quotes
	q_path = os.path.join(args.save_dir, 'quotations.txt')
	save_quotations(q_path, quotations)

	return

if __name__ == "__main__":
	args = parser.parse_args()
	main(args)

#EOF