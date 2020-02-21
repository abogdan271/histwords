import numpy as np
import os
import ioutils as util

from representations import sparse_io

def load_matrix(f):
    """Returns matrix from f as Compressed Sparse Column matrix"""
    if not f.endswith('.bin'):
        f += ".bin"
    return sparse_io.retrieve_mat_as_coo(f).tocsr()

def save_vocabulary(path, vocab):
    """Saves 'vocab' in 'path'"""
    with open(path, 'w') as f:
        for w in vocab:
            print >>f, w

def load_vocabulary(mat, path):
    """Loads index from path + "-index.pkl" sorts words by their ids and return the first mat.shape[0] elements and the first mat.shape[1] elements in two different lists."""
    if os.path.isfile(path.split(".")[0] + "-index.pkl"):
        path = path.split(".")[0] + "-index.pkl"
    else:
        print "Could not find local index. Attempting to load directory wide index..."
        path = "/".join(path.split("/")[:-1]) + "/merged_index.pkl"
    index = util.load_pickle(path)
    vocab = sorted(index, key = lambda word : index[word])
    iw = vocab[:mat.shape[0]]
    ic = vocab[:mat.shape[1]]
    return iw, ic
