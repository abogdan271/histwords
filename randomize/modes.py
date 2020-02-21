import numpy as np
from numpy.random import randint, choice
from scipy.sparse import dok_matrix as dm
from collections import defaultdict
import time

from representations import sparse_io

def exchange(dok_matrix):
    """Exchanges the matrix elements with each other"""
    print "this is randomization 'exchange'"
    new_dok_matrix = dm(dok_matrix.shape)
    values = dok_matrix.values()
#    coords = array([randint(0, dok_matrix.shape[0], len(dok_matrix)), randint(0, dok_matrix.shape[1], len(dok_matrix))]).T
#    print "coordinates are generated."
    t = time.time()
    i = 0
    j = 0
    while i < len(dok_matrix):
        new_row = randint(0, dok_matrix.shape[0])
        new_col = randint(0, dok_matrix.shape[1])
        while new_dok_matrix[new_row, new_col] != 0:
            new_row = randint(0, dok_matrix.shape[0])
            new_col = randint(0, dok_matrix.shape[1])
            j+= 1
        new_dok_matrix[new_row, new_col] = values[i]
        if i % 10000 == 0:
            print i, "done out of", len(dok_matrix), time.time() - t, j
        i += 1
    return new_dok_matrix

def sum_prop(dok_matrix):
    """Keeps the total number of each word but changes the co-occurence data."""
    print "this is randomization 'sum_prop'."
    new_dok_matrix = dm(dok_matrix.shape)
    all_counts = dok_matrix.sum()
    row_sums = dm(dok_matrix.sum(1)).items()
    column_sums = dm(dok_matrix.sum(0)).items()
    print "element probabilities counted. sum of occurrence:", all_counts
#    p_row = (row_sums/all_counts).transpose().tolist()[0]
#    p_column = (column_sums/all_counts).tolist()[0]
#    coords = np.array([choice(dok_matrix.shape[0], size=int(all_counts), p=p_row), choice(dok_matrix.shape[1], size=int(all_counts), p=p_column)]).T
    t = time.time()
    i = 0
    rows = defaultdict(int)
    cols = defaultdict(int)
    while i < int(all_counts):
        r1 = randint(0, len(row_sums))
        r2 = randint(0, len(column_sums))
        row = row_sums[r1][0][0]
        column = column_sums[r2][0][1]
        rows[row_sums[r1][0]] += 1
        cols[column_sums[r2][0]] += 1
        if row_sums[r1][1] - rows[row_sums[r1][0]] == 0:
            row_sums.pop(r1)
        if column_sums[r2][1] - cols[column_sums[r2][0]] == 0:
            column_sums.pop(r2)
#        row = choice(dok_matrix.shape[0], p=p_row)
#        col = choice(dok_matrix.shape[1], p=p_column)
        new_dok_matrix[row, column] += 1
        if i % 10000 == 0:
            print i, 'done of', all_counts, time.time() - t
        i += 1
    return new_dok_matrix
    
def uniform(dok_matrix):
    """Fill the matrix elements with numbers from uniform distribution"""
    print "this is randoization 'uniform'"
    new_dok_matrix = dm(dok_matrix.shape)
    row_sums = dok_matrix.sum(1)
    t = time.time()
    rows = list()
    all_counts = 0
    i = 0
    while i < row_sums.shape[0]:
        if row_sums[i, 0] > 400:
            rows += [i]
            all_counts += row_sums[i, 0]
        i += 1
    print "occurrences counted."
    t = time.time()
    i = 0
    while i < int(all_counts):
        row = rows[randint(0, len(rows))]
        col = rows[randint(0, len(rows))]
        new_dok_matrix[row, col] += 1
        if i % 10000 == 0:
            print i, "done of", all_counts, time.time() - t
        i += 1
    return new_dok_matrix

def randomize(infile, mode, outfile):
    """Betolti a coocurence matrixot, es a mode-nak megfeleloen randomizalja azaelemeit"""
    dok_matrix = sparse_io.retrieve_mat_as_coo(infile).todok()
    print "matrix loaded and converted to dok."
    dok_matrix = mode(dok_matrix)
    print "randomization done. writing..."
    sparse_io.export_mat_from_dict(dok_matrix, outfile)
    print "success"
