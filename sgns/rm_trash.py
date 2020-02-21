# Removes unnecessary files of embedding to save disk space.
# e.g. python -m sgns.rm_trash data_dir/embedding/noinit/300/ --workers 5 --start-year 1800 --end-year 1990

import os
from multiprocessing import Queue, Process
from argparse import ArgumentParser

def worker(proc_num, queue, dir):
    while True:
        if queue.empty():
            break
        year = queue.get()
        print "Removing data..", year
        time.sleep(0.01) # It is needed to eliminate unstability
        os.remove(dir + str(year) + "-c.bin")
        os.remove(dir + str(year) + "-c.npy")
        os.remove(dir + str(year) + "-c.txt")
        os.remove(dir + str(year) + "-w")
        os.remove(dir + str(year) + "-w.bin")
        os.remove(dir + str(year) + "-w.txt")

if __name__ == "__main__":
    parser = ArgumentParser("Removes files that are not used for analysis")
    parser.add_argument("dir")
    parser.add_argument("--workers", type=int, help="Number of processes to spawn", default=20)
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    parser.add_argument("--year-inc", type=int, default=1)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=worker, args=[i, queue, args.dir + "/"]) for i in range(args.workers)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
