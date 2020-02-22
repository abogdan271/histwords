# Merges the co-occurrence data from the alphabetically separated directories. Execution with runmerge.py. (Processes years that are contained in year!!!)
# Modified by Bogdan Asztalos

import collections
import os
import random
from multiprocessing import Process, Lock

from googlengram import indexing
from representations import sparse_io
import ioutils

def main(proc_num, lock, out_dir, in_dir, years):
    print proc_num, "Start loop"
    years.reverse()
    while True:
        lock.acquire()
        work_left = False
        # Iterates through the years (in a so complicated way)
        for year in years: 
            dirs = set(os.listdir(out_dir))
            if str(year) + ".bin" in dirs: # Checks if the individual year exists in the target directory. If it doesn't, allows the merging
                continue
            
            work_left = True
            print proc_num, "year", year
            fname = out_dir + str(year) + ".bin"
            with open(fname, "w") as fp:
                fp.write("")
            fp.close()
            break
        lock.release()
        if not work_left:
            print proc_num, "Finished"
            break

        print proc_num, "Merging counts for year", year # Merging starts here
        full_counts = collections.defaultdict(float)
        merged_index = collections.OrderedDict()
        for chunk_num in os.listdir(in_dir): # Iterates through the alphabetically separated co-occurrence data
            chunk_name = in_dir + str(chunk_num) + "/" + str(year) + ".bin"
            if not os.path.isfile(chunk_name):
                continue
            chunk_counts = sparse_io.retrieve_mat_as_coo(chunk_name)
            chunk_index = ioutils.load_pickle(in_dir + str(chunk_num) + "/index.pkl") 
            chunk_index = list(chunk_index)
            for pair, count in chunk_counts.todok().iteritems(): # Iterates through the co-occurrence matrices and add the occurrence of the word-pairs to the merged co-occurrence matrix
                i_word = chunk_index[pair[0]]
                c_word = chunk_index[pair[1]]
                new_pair = (indexing.word_to_cached_id(i_word, merged_index), 
                        indexing.word_to_cached_id(c_word, merged_index))
                full_counts[new_pair] += count
        
        print proc_num, "Writing counts for year", year
        sparse_io.export_mat_from_dict(full_counts, out_dir + str(year) + ".bin") # Saves the yearly merged co-occurrence matrices.
        ioutils.write_pickle(merged_index, out_dir + str(year) + "-index.pkl") # ... and the merged index
        ioutils.write_pickle(list(merged_index), out_dir + str(year) + "-list.pkl")

def run_parallel(num_procs, out_dir, in_dir, years):
    ioutils.mkdir(out_dir)
    lock = Lock()
    procs = [Process(target=main, args=[i, lock, out_dir + "/", in_dir + "/", years]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()   
