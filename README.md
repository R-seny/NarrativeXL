# NarrativeXL
Authors: Arseny Moskvichev, Ky-Vinh Mai

This repository accompanies the "NarrativeXL: a Large-scale Dataset for Long-Term Memory Models" paper: [https://arxiv.org/abs/2305.13877](https://arxiv.org/abs/2305.13877). If you use this resource, please cite us :) If you have any questions feel free to reach out (my email can be found in the paper).

## Dataset summary
NarrativeXL is a large-scale (nearly a million questions) extremely-long-context (more than 50,000 words average document length) reading comprehension dataset. With 990,595 total questions, NarrativeXL is an order of magnitude larger than the closest alternatives. Crucially, most questions have a known ``retention demand'', indicating how long-term of a memory is needed to answer them, which should aid long-term memory performance evaluation. We validate our data in four small-scale experiments: one with human labelers, and three with existing language models. We show that our questions 1) adequately represent the source material 2) can be used to diagnose a model's memory capacity 3) are not trivial for modern language models even when the memory demand does not exceed those models' context lengths. Lastly, we provide our code which can be used to further expand the dataset with minimal human labor.

![image](https://github.com/R-seny/NarrativeXL/assets/68800355/0050f754-5bb9-44a2-8492-a814d0fe3963)

## How to get the data?

Questions are stored in a CSV-like format with multi-symbol separators, to avoid potential quote, comma, etc. escaping issues. See utils/helper_functions.py for data loading examples.

Data download link: https://osf.io/4nz6x
IMPORTANT: the archive is password-protected to avoid accidental data contamination via web scraping. The password is the name of the paper (up to ":").


## What's in the data archive?

Qeustions/ folder contains multiple-choice read-along questions. Questions are stored in a CSV-like format with multi-symbol separators, to avoid potential quote, comma, etc. escaping issues. The file settings.py contains column, row, and a special separator for the case when one cell contains more than one entry (e.g. most book chunks are associated with three multiple-choice questions).

**See utils/helper_functions.py for a data loading example.**

Questions have substituted and raw versions, referring to whether or not Named Entity Substitution was performed. We suggest using the "substituted" version by default (see paper for more detais).

TrueAndFalseSummaries/ contains processed books, with columns being original book chunk, overlapped book chunk (up to 300 symbols, to avoid cases where important things are split mid-sentence between different chunks, true chunk summary, and false chunk summaries (note that some chunks (especially early in the book) might have more than one false summary).

HierarchicalSummaries/ contains summaries and hierarchical summaries for each book, with no raw book data.

CharacterSubstitution/ contains two pickle-created dictionaries for each book: one with character substitution maps (original book named entities mapped to random substitutions), and the other with original book named entity counts.

## If you want to dig deeper/replicate our results:

Main functions:

gpt_api_processing.py - Main functions with openai API wrappers for summarization, summary distortion, hierarchical summarization, etc.

anthropic_performance_test.py - code for testing GPT and Anthropic model performance on our data.

QualityTestBert.py - code for BERT-based testing of "change"-type multiple-choice questions.

Dataloaders.py - structures for book processing.

ProcessBooks.py - main script to process a book folder, creating true and false hierarchical summaries. Assumes that books are pre-processed and cleaned (i.e. boilerplate Gutenberg information removed).

CreateHiararchicalSummaries - create hierarchical summaries (requires books to be already processed).

AddDistortedHierarchicalSummaries - adds distorted summaries to the result of the script above.

settings.py - Contains parameters for a) data saving (all data is saved in CSV-like format but with custom line and column separators) b) question generation (how many questions per step, etc.) c) Book chunking, specifically, overlap between subsequent book chunks.

character_list_generator.py - contains important classes for generating character substitution lists. Goes through the entire text file and searches and gathers all of the entity names. Produces a json file with all the character names and their randomized label names.

PrepareCharacterSubDicts.py allows one to create charater list for each .tag_separated file. First specify the folder that contains the .tag_separated files in sum_paths and the folder in which to save it, in the results_folder.

entity_replacement.py can be used directly on files and directories. However, it is primarily is used by other parts of our program, Ex. question-generator utilizes some of its functions (i.e. you don't have to worry about directly running it). Applies pre-made character substitution dictionaries to arbitrary text documents.

## If you want to expand the dataset:

The general usage pipeline is 
0) Pre-process raw books (remove Gutenberg boilerplate info, etc.)
1) Run ProcessBooks.py (creates non-hierarchical true and false summaries).
2) Run PrepareCharacterSubDicts.py to create named entity substitution dictionaries that will be later used by the QuestionGeneration script.
3a) Run QuestionGeneration.py to generate multiple choice scene recognition questions.
3b) For scene reconstruction questions, run CreateHiararchicalSummaries.py and then AddDistortedHierarchicalSummaries.py
