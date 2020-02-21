# Execute the merge.py which merges the co-occurrence data from the alphabetically separated directories. (It's needed to give 1 to year-inc, because merge.py processes only years that are contained in variable 'years')
# e.g. python -m googlengram.pullscripts.runmerge data_dir/merged/ data_dir/unmerged/c2/raw/ 5 --start-year 1800 --end-year 1999 --year-inc 1

import argparse
from googlengram.pullscripts.merge import run_parallel

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merges years of raw 5gram data.")
    parser.add_argument("out_dir", help="directory where data will be stored")
    parser.add_argument("in_dir", help="path to unmerged data")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("--start-year", type=int, default=1700)
    parser.add_argument("--end-year", type=int, default=2000)
    parser.add_argument("--year-inc", type=int, default=1)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    run_parallel(args.num_procs, args.out_dir, args.in_dir, years)       

