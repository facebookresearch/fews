# FEWS: Few-shot Examples of Word Sense

This is the codebase for the [FEWS (Few-shot Examples of Word Sense)](https://nlp.cs.washington.edu/fews/) dataset. This code will allow you to replicate the data creation process, given a Wiktionary dump .xml file. The README for the dataset itself is in dataset_README.txt.

## How to Run
To create the dataset with a given Wiktionary dump .xml file, run `bash create_dataset.sh <WIKI_FILE_PATH>`. FEWS was created with the 01/01/2020 Wiktionary dump (which is no longer available on the WikiMedia checkpoint page, but similar checkpoints of Wiktionary can be found [here](https://dumps.wikimedia.org/backup-index.html)). We use the "Articles, templates, media/file descriptions, and primary meta-pages" version. This code needs [Python 3](https://www.python.org/) to run.

## Citation
If you use this codebase or the resulting dataset, please cite the corresponding [paper](https://blvns.github.io/papers/eacl2021.pdf): 
```
@inproceedings{ 
	blevins2021fews,
	title={FEWS: Large-Scale, Low-Shot Word Sense Disambiguation with the Dictionary},
	author={Terra Blevins and Mandar Joshi and Luke Zettlemoyer},
	booktitle={Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics},
	year={2021},
	url={https://blvns.github.io/papers/eacl2021.pdf}
}
```

## Contact
Please address any questions or comments about this codebase to blvns@cs.washington.edu. If you want to suggest changes or improvements, please check out the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.

## License
This codebase is Attribution-NonCommercial 4.0 International licensed, as found in the [LICENSE](https://github.com/facebookresearch/fews/blob/master/LICENSE) file.