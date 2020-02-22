# Creates a merged index for all years. Drops out words that contain non alphabetic character and stopwords
# e.g. python -m googlengram.pullscripts.indexmerge data_dir/index_merged/ data_dir/merged/ english --start-year 1800 --end-year 1999 --year-inc 1
# Modified by Bogdan Asztalos

import collections
import argparse
from nltk.corpus import stopwords

from googlengram import indexing
import ioutils

def run(out_dir, in_dir, years, language):
    index = collections.OrderedDict()
    for year in years: # Iterates through the year
        print "Merging year", year
        year_list = ioutils.load_pickle(in_dir + str(year) + "-list.pkl")
        i = 0
        for i in xrange(len(year_list)): # Iterates through the words in the individual year
            word = year_list[i]
            stop_set = set(stopwords.words(language))
            if word.isalpha() and not word in stop_set:
                indexing.word_to_cached_id(word, index) # Put every word in the common index

    ioutils.mkdir(out_dir)
    ioutils.write_pickle(index, out_dir + "merged_index.pkl") 
    ioutils.write_pickle(list(index), out_dir + "merged_list.pkl") 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Makes merged index for cooccurrence data")
    parser.add_argument("out_dir", help="directory where merged index will be stored")
    parser.add_argument("in_dir", help="path to unmerged data")
    parser.add_argument("language", help="language of corpus")
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    parser.add_argument("--year-inc", type=int, default=1)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    run(args.out_dir + "/", args.in_dir + "/", years, args.language)
