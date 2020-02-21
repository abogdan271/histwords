# Recreates the merged co-occurrence matrices with the merged index, that was created by the indexmerge.py. Drops out words that contain non alphabetic character and stopwords
# e.g. python -m googlengram.pullscripts.countmerge data_dir/index_merged/ data_dir/merged/ 5 --start-year 1800 --end-year 1999 --year-inc 1

import sys
import argparse
from Queue import Empty 
from multiprocessing import Process, Queue

from googlengram import indexing
from representations import sparse_io
import ioutils

def main(proc_num, queue, out_dir, in_dir):
    merged_index = ioutils.load_pickle(out_dir + "merged_index.pkl") 
    print proc_num, "Start loop"
    while True: # Iterates through the years
        try: 
            year = queue.get(block=False)
        except Empty:
            print proc_num, "Finished"
            break
        print proc_num, "Fixing counts for year", year
        fixed_counts = {} # This is the new co-occurrence matrix
        old_mat = sparse_io.retrieve_mat_as_coo(in_dir + str(year) + ".bin").todok()
        old_index = ioutils.load_pickle(in_dir + str(year) + "-list.pkl") 
        for pair, count in old_mat.iteritems(): # Iterates through the unmerged co-occurrence matrix ...
            try:
                i_word = old_index[pair[0]]
            except IndexError:
                print pair
                sys.exit(0)
            c_word = old_index[pair[1]]
            try:
                new_pair = (indexing.word_to_static_id(i_word, merged_index), 
                        indexing.word_to_static_id(c_word, merged_index))
            except KeyError: # Filters words to drop out
                continue
            fixed_counts[new_pair] = count # ... and add the counts to the new one
        
        print proc_num, "Writing counts for year", year # Saves the new co-occurrence matrices
        sparse_io.export_mat_from_dict(fixed_counts, out_dir + str(year) + ".bin")

def run_parallel(num_procs, out_dir, in_dir, years):
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=main, args=[i, queue, out_dir, in_dir]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Converts yearly counts to have merged index.")
    parser.add_argument("out_dir", help="directory where the consolidated data will be stored. Must also contain merged index.")
    parser.add_argument("in_dir", help="path to unmerged data")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    parser.add_argument("--year-inc", type=int, default=1)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    run_parallel(args.num_procs, args.out_dir + "/", args.in_dir + "/", years)
