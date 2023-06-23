# NarrativeXL
Authors: Arseny Moskvichev, Ky-Vinh Mai

## Introduction

This repository accompanies the "NarrativeXL: A Large-scale Dataset For Long-Term Memory Models" paper. Data .zip-file is password-protected to avoid unintentional data contamination through web-scraping. The password coincides with the paper name (up to ":").

##Abstract
Most large language models rely on their context window as their only memory mechanism; consequently, after initial training, they can not internalize new information in the long-term. Overcoming this limitation would not only require changes to the typical transformer architectures or training procedures, but also a dataset on which long-term memory models could be trained and evaluated. We argue that existing resources lack a few key properties, and that at present, there are no naturalistic datasets of sufficient scale to train (and not only evaluate) long-term memory language models. We then present our solution that capitalizes on the advances in short a-term memory language modeling to create such a dataset. Using GPT 3.5, we summarized each scene in 1500 hand-curated fiction books from Project Gutenberg, which resulted in $\sim$150 scene-level summaries per book. After that, we created a number of reading comprehension questions based on these summaries, including three types of multiple-choice scene recognition questions, as well as free-form narrative reconstruction questions. With ~500 reading comprehension questions per book, our dataset is an order of magnitude larger than closest alternatives. Crucially, most questions have a known `retention demand', indicating how long-term of a memory is needed to answer it, which should aid long-term memory performance evaluation. We validate our data in four small-scale experiments: one with human labelers, and three with existing language models. We show that our questions 1) adequately represent the source material 2) can be used to diagnose a model's memory capacity 3) are not trivial for modern language models even when the memory demand does not exceed those models' context lengths. Lastly, we provide our code which can be used to further expand the dataset with minimal human labor.


Train data link: https://osf.io/rxjsc

Questions are stored in a CSV-like format with multi-symbol separators, to avoid potential quote, comma, etc. escaping issues. See utils/helper_functions.py for a data loading example.

We plan to release a more complete codebase and more data in the near future.
Please contact me if you have any questions (the email can be found in the arXiv paper).
