# Diachronic Word2vec Embedding from Google Ngrams data

### Author: Bogdan Asztalos (abogdan@caesar.elte.hu)
### Based on William Hamilton's (wleif@stanford.edu) code: [Original Repository](https://github.com/williamleif/histwords)

## Overview 

In `googlengram`, `sgns` and `vecanalysis` directories a collection of programs can be found to create diachronic word embedding with Word2vec. The code is a developed and (in some cases) modifyed version of William Hamilton's code for historical word embeddings.

## Creating embedding

The code is optimized for downloading data from Google Ngram Viewer and training Word2vec embeddings for different time intervals. Bash script `full_process.sh` executes all the necessary codes.

### Embedding process

The embedding process introduced in `full_process.sh` differs from the original code in three main point:
* Stems (lemmatizes) the words and embeds the root of words together
* Embeds only words selected by given rules, and creates equal number of data for training the embedding, regardless of the quantity of raw data
* For a given time interval trains more embedding and get the avarage of them

## Code organization

Most of the original code is untouched. In `googlengram`, `sgns`, `vecanalysis` directiories and in a few other files some debuggings and modifies did happen.

The structure of the code (in terms of folder organization) is as follows:

Main folder for using historical embeddings:
* `representations` contains code that provides a high-level interface to (historical) word vectors and is originally based upon Omer Levy's hyperwords package (https://bitbucket.org/omerlevy/hyperwords).

Folders with pre-processing code and active research code (potentially unstable):
* `googlengram` contains code for pulling and processing historical Google N-Gram Data (http://storage.googleapis.com/books/ngrams/books/datasetsv2.html).
* `coha` contains code for pulling and processing historical data from the COHA corpus (http://corpus.byu.edu/coha/).
* `statutils` contains helper code for common statistical tasks.
* `vecanalysis` contains code for evaluating and analyzing historical word vectors.
* `sgns` contains a modified version of Google's word2vec code (https://code.google.com/archive/p/word2vec/)

## Dependencies

Core dependencies:
  * python 2.7
  * sklearn: http://scikit-learn.org/stable/
  * cython: http://docs.cython.org/src/quickstart/install.html
  * statsmodels: http://statsmodels.sourceforge.net/

You will also need Juptyer/IPython to run any IPython notebooks.
