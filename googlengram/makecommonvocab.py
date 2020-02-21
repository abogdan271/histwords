# Creates a vocabulary containing words that occure in every year more than the given limit
# e.g. python -m googlengram.makecommonvocab data_dir/decades/ data_dir/decades/ data_dir/counts/ --start-year 1800 --end-year 1990 --year-inc 1

import argparse

import ioutils

def main(years, out_dir, in_dir, count_dir, min_count, num_words):
    print "Making common vocab"
    words = ioutils.load_pickle(in_dir + str(years[0]) + "-list.pkl")
    for year in years:
        counts_year = ioutils.load_pickle(count_dir + str(year) + "-counts.pkl")
        use_words = sorted(counts_year.keys(), key = lambda word : counts_year[word])[:num_words]
        use_words = [word for word in use_words if counts_year[word] > min_count]
        i = 0
        while i < len(words):
            if words[i] not in use_words:
                words.pop(i)
                i -= 1
            i += 1
        print year, "vocab, done"

    ioutils.write_pickle(list(words), out_dir + "common_vocab.pkl")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates a vocabulary containing words that occure in every year")
    parser.add_argument("out_dir", help="output directory. Must be existed")
    parser.add_argument("in_dir", help="directory where the co-occurence matrices are placed")
    parser.add_argument("count_dir", help="directory where the count data are placed")
    parser.add_argument("--start-year", type=int, default=1900, help="start year (inclusive)")
    parser.add_argument("--end-year", type=int, default=2000, help="end year (inclusive)")
    parser.add_argument("--year-inc", type=int, default=1)
    parser.add_argument("--min-count", type=int, default=100, help="the minimum count to not ignore a word")
    parser.add_argument("--num-words", type=int, default=None, help="maximum number of words (optional)")
    args = parser.parse_args()

    years = range(args.start_year, args.end_year + 1)
    main(years, args.out_dir + "/", args.in_dir + "/", args.count_dir + "/", args.min_count, args.num_words)
