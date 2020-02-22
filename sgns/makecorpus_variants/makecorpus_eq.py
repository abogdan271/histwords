# Modification os makecorpus.py: Uses only given words + creates a given number of word pair data
# e.g. python -m sgns.makecorpus_eq data_dir/corpus/ data_dir/decades/ data_dir/counts/ data_dir/common_vocab.pkl
# Modified by Bogdan Asztalos

import argparse
import os
import numpy as np

from multiprocessing import Process, Queue
from Queue import Empty

import ioutils
from representations.explicit import Explicit

def worker(proc_num, queue, out_dir, in_dir, use_words, count_dir, num_sam, sample=1e-5):
    while True:
        try:
            year = queue.get(block=False)
        except Empty:
            break
        print proc_num, "Getting counts and matrix year", year
        embed = Explicit.load(in_dir + str(year) + ".bin", normalize=False) # Loads embedding and its count data
        embed = embed.get_subembed(use_words, restrict_context=True) # Restricts the vocabulary to given words
        counts = ioutils.load_pickle(count_dir + "/" + str(year) + "-counts.pkl")
        all_count = sum(counts.values())
        mat = embed.m.tocoo()
        print proc_num, "Outputing pairs for year", year
        with open(out_dir + str(year) + ".tmp.txt", "w") as fp:
            for i in xrange(len(mat.data)): # Iterates through the occured word pairs
                if i % 10000 == 0:
                    print "Done ", i, "of", len(mat.data)
                word = embed.iw[mat.row[i]]
                context = embed.ic[mat.col[i]]
                if sample != 0:
                    prop_keep = min(np.sqrt(sample / counts[word] * all_count), 1.0) 
                    prop_keep *= min(np.sqrt(sample / counts[context] * all_count), 1.0) 
                else:
                    prop_keep = 1.0
                word = word.encode("utf-8")
                context = context.encode("utf-8")
                line = word + " " + context + "\n"
                for j in xrange(int(mat.data[i] * prop_keep)): # Writes down the word pair as many times as it is needed
                    fp.write(line)
        mat = mat.tocsr()
        print proc_num, "Outputing vocab for year", year
        with open(out_dir + str(year) + ".vocab", "w") as fp:
            for word in use_words:
                print >>fp, word.encode("utf-8"), int(mat[embed.wi[word], :].sum())
        print "shuf " + out_dir + str(year) + ".tmp.txt" " > " + out_dir + str(year) + ".txt" 
        os.system("shuf " + out_dir + str(year) + ".tmp.txt -r -n " + str(num_sam) + " > " + out_dir + str(year) + ".txt") # Sampling randomly from the word pairs as many times as is given
        os.remove(out_dir + str(year) + ".tmp.txt")

def run_parallel(num_procs, out_dir, in_dir, years, wordlist, count_dir, num_sam, sample):
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=worker, args=[i, queue, out_dir, in_dir, wordlist, count_dir, num_sam, sample]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Computes various frequency statistics.")
    parser.add_argument("out_dir")
    parser.add_argument("in_dir")
    parser.add_argument("count_dir")
    parser.add_argument("wordlist")
    parser.add_argument("--num_sam", type=int, default=10000000)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--start-year", type=int, help="start year (inclusive)", default=1800)
    parser.add_argument("--end-year", type=int, help="end year (inclusive)", default=2000)
    parser.add_argument("--year-inc", type=int, help="end year (inclusive)", default=1)
    parser.add_argument("--sample", type=float, default=1e-5)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    ioutils.mkdir(args.out_dir)
    wordlist = ioutils.load_pickle( args.wordlist )
    run_parallel(args.workers, args.out_dir + "/", args.in_dir + "/", years, wordlist, args.count_dir, args.num_sam, args.sample)
