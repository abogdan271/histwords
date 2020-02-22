# Creates two files: ..._.pkl contains a dict mapping year to words that are occured in that year (in descending order of occurrence). ...-freqs.pkl contains a dict mapping word to year-occurrence pairs. (if a word didn't occure in a year, it's occurrence is 'nan'). (If the occurrence of a word in an individual year is lesser than 10**-7, it isn't counted)
# e.g. python -m googlengram.freqperyear /home/asztalosb/datas/freqperyear/c2/ /home/asztalosb/datas/indexed_merged/c2/ 1 --start-year 1800 --end-year 1999 
# Modified by Bogdan Asztalos
# MAY BE UNSTABLE

import argparse
import os
import random
import collections
from Queue import Empty 
from multiprocessing import Process, Queue

#from nltk.corpus import stopwords

import ioutils
from representations import sparse_io

def merge(years, out_pref, out_dir):
    word_freqs = collections.defaultdict(dict) # dict mapping year to word-relative_frequency pairs
    word_lists = {} # dict mapping year to list of used words
    word_set = set([]) # set of words ever used
    for year in years: # Collects word_lists
        word_lists[year] = ioutils.load_pickle(out_dir + str(year) + "tmp.pkl")
        word_set = word_set.union(set(word_lists[year]))
        os.remove(out_dir + str(year) + "tmp.pkl")
    for year in years: # Collects relative frequencies
        year_freqs= ioutils.load_pickle(out_dir + str(year) + "freqstmp.pkl")
        for word in word_set:
            if word not in year_freqs:
                word_freqs[word][year] = float('nan')
            else:
                word_freqs[word][year] = year_freqs[word]
        os.remove(out_dir + str(year) + "freqstmp.pkl")

    ioutils.write_pickle(word_freqs, out_pref + "-freqs.pkl") # Saves relative frequencies
    ioutils.write_pickle(word_lists, out_pref + ".pkl") # Saves word_lists

def main(proc_num, queue, out_pref, out_dir, in_dir, index, freq_thresh, lang):
    #random.shuffle(years) # I don't know what it is for
    print proc_num, "Start loop"
    while True: # Iterates through the years
        try: 
            year = queue.get(block=False)
        except Empty:
            print proc_num, "Finished"
            break
        #stop_set = set(stopwords.words(lang))
        word_freqs = {} # dict with word-relative_freq pairs
        print "Loading mat for year", year
        year_mat = sparse_io.retrieve_mat_as_coo(in_dir + str(year) + ".bin")
        year_mat = year_mat.tocsr()
        year_mat = year_mat / year_mat.sum() # normalizes the co-occurrence matrix
        print "Processing data for year", year
        for word_i in xrange(year_mat.shape[0]):
            word = index[word_i]
            if not word.isalpha():# or word in stop_set or len(word) == 1: # filters out the degenerated words
                continue 
            year_freq = year_mat[word_i, :].sum() # thank to the normalization it's the relative frequency of the word
            word_freqs[word] = year_freq
        print "Writing data"
        sorted_list = sorted(word_freqs.keys(), key = lambda key : word_freqs[key], reverse=True) # sorting and filtering
        sorted_list = [word for word in sorted_list 
                    if word_freqs[word] > freq_thresh]
        ioutils.write_pickle(sorted_list, out_dir + str(year) + "tmp.pkl") # Saves the list of words
        ioutils.write_pickle(word_freqs, out_dir + str(year) + "freqstmp.pkl") # Saves the relative frequencies

def run_parallel(num_procs, years, out_pref, out_dir, in_dir, index, freq_thresh, lang):
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=main, args=[i, queue, out_pref, out_dir, in_dir, index, freq_thresh, lang]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    merge(years, out_pref, out_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get yearly sorted by-frequency list of (non-stop) words and dicts with their frequencies")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("in_dir", help="directory with 5 grams and index")
    parser.add_argument("num_procs", type=int, help="num procs")
    parser.add_argument("--start-year", type=int, default=1900, help="start year (inclusive)")
    parser.add_argument("--end-year", type=int, default=2000, help="end year (inclusive)")
    parser.add_argument("--freq-thresh", type=int, default=7, help="frequency threshold (neg. power of 10)")
    parser.add_argument("--lang", type=str, default="english", help="language")
    args = parser.parse_args()

    years = range(args.start_year, args.end_year + 1)
    index = ioutils.load_pickle(args.in_dir + "/merged_list.pkl")
    out_pref = args.out_dir + "/freqnonstop_peryear-" + str(years[0]) + "-" + str(years[-1]) + "-"  + str(args.freq_thresh)
    freq_thresh = 10.0 ** (-1.0 * float(args.freq_thresh))
    run_parallel(args.num_procs, years, out_pref , args.out_dir + "/", args.in_dir + "/", index, freq_thresh, args.lang)
