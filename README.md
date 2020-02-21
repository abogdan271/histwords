# Word Embeddings for Historical Text

### Original Author: William Hamilton (wleif@stanford.edu)
### [Original Repository](https://github.com/williamleif/histwords)
### Co-Author: Bogdan Asztalos (abogdan@caesar.elte.hu)

## Overview 

Collection of programs to create diachronic word embedding with Word2vec. This code is a developed and (in some cases) modifyed version of William Hamilton's code.

## Creating embedding

The code is optimized for downloading data from Google Ngram Viewer and training Word2vec embeddings for different time intervals. Bash script `full_process.sh` will execute all the necessary codes.

### Embedding process

The embedding process introduced in `full_process.sh` differs from the original code in three main point:
* Stems (lemmatizes) the words and embeds the root of words together
* Embeds only words selected by given rules, and creates equal number of data for training the embedding, regardless of the quantity of raw data
* For a given time interval trains more embedding and get the avarage of them

## Code organization

Most of the original code is untouched. In `googlengram`, `sgns` and `vecanalysis` directiories some debuggings and modifies did happen.

The structure of the code (in terms of folder organization) is as follows:

Main folder for using historical embeddings:
* `representations` contains code that provides a high-level interface to (historical) word vectors and is originally based upon Omer Levy's hyperwords package (https://bitbucket.org/omerlevy/hyperwords).

Folders with pre-processing code and active research code (potentially unstable):
* `googlengram` contains code for pulling and processing historical Google N-Gram Data (http://storage.googleapis.com/books/ngrams/books/datasetsv2.html).
* `coha` contains code for pulling and processing historical data from the COHA corpus (http://corpus.byu.edu/coha/).
* `statutils` contains helper code for common statistical tasks.
* `vecanalysis` contains code for evaluating and analyzing historical word vectors.
* `sgns` contains a modified version of Google's word2vec code (https://code.google.com/archive/p/word2vec/)

<!---`statistical-laws.ipynb` contains an IPython notebook with the main code necessary for replicating the key results of our [published work](http://arxiv.org/abs/1605.09096).--->

`example.py` shows how to compute the simlarity series for two words over time, which is how we evaluated different methods against the attested semantic shifts listed in our paper. 

If you want to learn historical embeddings for new data, the code in the `sgns` directory is recommended, which can be run with the default settings. As long as your corpora has at least 100 million words per time-period, this is the best method. For smaller corpora, using the `representations/ppmigen.py` code followed by the `vecanalysis/makelowdim.py` code (to learn SVD embeddings) is recommended. In either case, the `vecanalysis/seq_procrustes.py` code should be used to align the learned embeddings. The default hyperparameters should suffice for most use cases. 

However, as a caveat to the above, the code is somewhat messy, unstable, and specific to the historical corpora that it was originally designed for. If you are looking for a nice, off-the-shelf toolbox to run word2vec, I recommend you check out [gensim](https://radimrehurek.com/gensim/models/word2vec.html). 

<!--- * `notebooks` contains notebooks useful for replicating my published results-->

<!--- *See REPLICATION.md for detailed instructions on how to replicate specific published/submitted results.-->

## Dependencies

Core dependencies:
  * python 2.7
  * sklearn: http://scikit-learn.org/stable/
  * cython: http://docs.cython.org/src/quickstart/install.html
  * statsmodels: http://statsmodels.sourceforge.net/

You will also need Juptyer/IPython to run any IPython notebooks.
