#Copyright (c) Facebook, Inc. and its affiliates.
#All rights reserved.
#This source code is licensed under the license found in the
#LICENSE file in the root directory of this source tree.


#Script to create FEWS dataset
#$1 -- uncompressed wiktionary dump filepath 

#make dir to store created dataset in
mkdir ./fews
mkdir ./fews/raw

#extracting data from wiktionary dump
python3 data_parsing.py --wiki-file "$1" --save-dir ./fews/raw
#spliting data into train/dev/test
python3 split_data.py --raw-dir ./fews/raw --save-dir ./fews
mv ./fews/raw/senses.txt ./fews/senses.txt

#restructure data files
mkdir ./fews/train
mv ./fews/train.txt ./fews/train/train.txt 
mv ./fews/train.ext.txt ./fews/train/train.ext.txt 

mkdir ./fews/dev
mv ./fews/dev.few-shot.txt ./fews/dev/dev.few-shot.txt 
mv ./fews/dev.zero-shot.txt ./fews/dev/dev.zero-shot.txt 

mkdir ./fews/test
mv ./fews/test.few-shot.txt ./fews/test/test.few-shot.txt 
mv ./fews/test.zero-shot.txt ./fews/test/test.zero-shot.txt 

mv ./fews/monosemous.txt ./fews/raw/monosemous.txt

#move python utils for loading/saving data to data folder
cp utils.py fews/dataset-utils.py
#move readme and datasheet into data folder
cp dataset_README.txt fews/README.txt
cp datasheet.pdf fews/datasheet.pdf

#EOF