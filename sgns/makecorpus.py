# Collects the occured word pairs in the format that can be processed by the word2vec
# e.g. python -m sgns.makecorpus data_dir/corpus/ data_dir/decades/ data_dir/counts/ --workers 5 --start-year 1800 --end-year 1990
# Modified by Bogdan Asztalos

import argparse
import os
import numpy as np

from multiprocessing import Process, Queue
from Queue import Empty

import ioutils
from representations.explicit import Explicit

def worker(proc_num, queue, out_dir, in_dir, num_words, min_count, count_dir, sample=1e-5):
    while True:
        try:
            year = queue.get(block=False)
        except Empty:
            break
        print proc_num, "Getting counts and matrix year", year
        embed = Explicit.load(in_dir + str(year) + ".bin", normalize=False) # Loads embedding and its count data
        counts = ioutils.load_pickle(count_dir + "/" + str(year) + "-counts.pkl")
        all_count = sum(counts.values())
        use_words = sorted(embed.iw, key = lambda word : counts[word])[:num_words] # Takes into count only words above the given limits
        use_words = [word for word in use_words if counts[word] > min_count]
        embed = embed.get_subembed(use_words, restrict_context=True)
        mat = embed.m.tocoo()
        print proc_num, "Outputing pairs for year", year
        with open(out_dir + str(year) + ".tmp.txt", "w") as fp:
            for i in xrange(len(mat.data)):  # Iterates through the occured word pairs
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
        os.system("shuf " + out_dir + str(year) + ".tmp.txt" + " > " + out_dir + str(year) + ".txt") # Shuffles the order of word pairs
        os.remove(out_dir + str(year) + ".tmp.txt")

def run_parallel(num_procs, out_dir, in_dir, years, num_words, min_count, count_dir, sample):
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=worker, args=[i, queue, out_dir, in_dir, num_words, min_count, count_dir, sample]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Computes various frequency statistics.")
    parser.add_argument("out_dir")
    parser.add_argument("in_dir")
    parser.add_argument("count_dir")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--num-words", type=int, default=None)
    parser.add_argument("--start-year", type=int, help="start year (inclusive)", default=1800)
    parser.add_argument("--end-year", type=int, help="end year (inclusive)", default=2000)
    parser.add_argument("--year-inc", type=int, help="end year (inclusive)", default=1)
    parser.add_argument("--min-count", type=int, default=100)
    parser.add_argument("--sample", type=float, default=1e-5)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    ioutils.mkdir(args.out_dir)
    run_parallel(args.workers, args.out_dir + "/", args.in_dir + "/", years, args.num_words, args.min_count, args.count_dir, args.sample)       
