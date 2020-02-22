# Funcitions to handle words and their indices.
# Modified by Bogdan Asztalos

import numpy as np

from nltk.stem import snowball

def word_to_id(word, index):
    """Returns the id of the well-formatted version of 'word'. If 'word' is not in 'index', puts it in, and returns the new id."""
    word = word.decode('utf-8').lower()
    word = word.strip("\"")
    word = word.split("\'s")[0]
    esb = snowball.EnglishStemmer()
    word = esb.stem(word)
    try:
        return index[word]
    except KeyError:
        id_ = len(index)
        index[word] = id_
        return id_

def word_to_cached_id(word, index):
    """
    Returns the id of 'word'. If 'word' is not in 'index', puts it in and returns the new id.
    !!! word must be well-formatted (unicode type and lemmatized) !!!
    """
    try:
        return index[word]
    except KeyError:
        id_ = len(index)
        index[word] = id_
        return id_

def word_to_static_id(word, index):
    """Returns the id of 'word'. If 'word' is not in 'index', throws KeyError."""
    return index[word]

def word_to_static_id_pass(word, index):
    """Returns the id of 'word'. If 'word' is not in 'index', returns -1."""
    try:
        return index[word]
    except KeyError:
        return -1;

def get_word_indices(word_list, index):
    """Returns a list of words in 'word_list' and their indices in an array (in the same order)."""
    common_indices = []
    new_word_list = []
    for word in word_list:
        try:
            common_indices.append(index[word])
            new_word_list.append(word)
        except KeyError:
            print "Unmapped word:", word
    return new_word_list, np.array(common_indices)

def get_full_word_list(year_indexinfo):
    """Returns a list of words used in years of 'year_indexinfo"."""
    word_set = set([])
    for info in year_indexinfo.values():
        word_set.update(info["list"])
    return list(word_set)
