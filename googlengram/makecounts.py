# Creates a .pkl file with the dict of occurrence of words
# e.g. python -m googlengram.makecounts data_dir/counts/ data_dir/decades/ 5 2 --start-year 1800 --end-year 1990

import argparse
from Queue import Empty 
from multiprocessing import Process, Queue

import ioutils
from representations.matrix_serializer import load_matrix

def main(proc_num, queue, out_dir, in_dir, context_size):
    ioutils.mkdir(out_dir)
    print proc_num, "Start loop"
    while True: # Iterates through the years
        try: 
            year = queue.get(block=False)
        except Empty:
            print proc_num, "Finished"
            break
        print proc_num, "- Loading mat for year", year
        year_mat = load_matrix(in_dir + str(year) + ".bin")
        index = ioutils.load_pickle(in_dir + str(year) + "-index.pkl")
        print proc_num, "- Processing data for year", year
        counts = year_mat.sum(1) / (2 * context_size) # sums up the occurrence
        counts = { word : int(counts[index[word]]) for word in index if index[word] < len(counts) }
        ioutils.write_pickle(counts, out_dir + "/" + str(year) + "-counts.pkl") # writes it in a file 

def run_parallel(num_procs, years, out_dir, in_dir, context_size):
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=main, args=[i, queue, out_dir, in_dir, context_size]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates a .pkl file with the dict of occurrence of words")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("in_dir", help="directory with 5 grams and index")
    parser.add_argument("num_procs", type=int, help="num procs")
    parser.add_argument("context_size", type=int)
    parser.add_argument("--start-year", type=int, default=1900, help="start year (inclusive)")
    parser.add_argument("--end-year", type=int, default=2000, help="end year (inclusive)")
    args = parser.parse_args()

    years = range(args.start_year, args.end_year + 1)
    run_parallel(args.num_procs, years, args.out_dir + "/", args.in_dir + "/", args.context_size)
