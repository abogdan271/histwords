# Creates decadely co-occurrence matrices from yearly co-occurrence matrices. (Every year must have own index.)
# e.g. python -m googlengram.makedecades data_dir/decades/ data_dir/index_merged/ 5 --start-year 1800 --end-year 1990 --year-inc 1

import argparse
import collections
import os

from multiprocessing import Process, Queue
from Queue import Empty

from googlengram.indexing import word_to_cached_id
from representations.explicit import Explicit
from representations.sparse_io import export_mat_from_dict
from ioutils import mkdir, write_pickle, load_pickle

def worker(proc_num, queue, out_dir, in_dir):
    while True: # Iterates through the decades
        try:
            decade = queue.get(block=False)
        except Empty:
            break

        print "Processing decade", decade
        counts = collections.defaultdict(int) # this dict represents the co-occurrence matrix      
        for year in range(10): # Iterates through the years in the decade
            embed = Explicit.load(in_dir + str(decade + year) + ".bin", normalize=False) # Makes an embedding about the individual year (here is needed the own index)
            if year == 0:
                merged_index = embed.wi
            if os.path.isfile(in_dir + str(decade + year) + "-list.pkl"):
                year_list = load_pickle(in_dir + str(decade + year) + "-list.pkl")
            else:
                year_list = load_pickle(in_dir + "merged_list.pkl")
            mat = embed.m.tocoo()
            for i in xrange(len(mat.data)): # Iterates through the word-context pairs and counts the co-occurrence 
                if mat.data[i] == 0:
                    continue
                new_row = word_to_cached_id(year_list[mat.row[i]], merged_index)
                new_col = word_to_cached_id(year_list[mat.col[i]], merged_index)
                counts[(new_row, new_col)] += mat.data[i] # Adds the co-occurrence to the decade-data
            print "Done year ", decade + year
        export_mat_from_dict(counts, out_dir + str(decade) + ".bin") # Saves the decadely co-occurrence matrix
        write_pickle(merged_index, out_dir + str(decade) + "-index.pkl") # Saves the decadely index
        write_pickle(list(merged_index), out_dir + str(decade) + "-list.pkl")

def run_parallel(num_procs, out_dir, in_dir, decades):
    queue = Queue()
    for decade in decades:
        queue.put(decade)
    procs = [Process(target=worker, args=[i, queue, out_dir, in_dir]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merges years of raw 5gram data.")
    parser.add_argument("out_dir", help="path to network data (also where output goes)")
    parser.add_argument("in_dir", help="path to network data (also where output goes)")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("--start-year", type=int, help="start year (inclusive)")
    parser.add_argument("--end-year", type=int, help="end year (inclusive)")
    parser.add_argument("--year-inc", type=int, default=10, help="difference two consecutive 'decade'")
    args = parser.parse_args()
    decades = range(args.start_year, args.end_year + 1, args.year_inc)
    decades.reverse()
    mkdir(args.out_dir)
    run_parallel(args.num_procs, args.out_dir + "/",  args.in_dir + "/", decades)       
