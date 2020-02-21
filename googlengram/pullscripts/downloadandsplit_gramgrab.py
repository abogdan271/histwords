# It runs downloadandsplit and gramgrab in the same execution, deletes the raw file and saves disk space
# e.g. python -m googlengram.pullscripts.downloadandsplit_gramgrab data_dir http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-fiction-all 2 5

import requests
import urllib2
import re
import os
import subprocess
import argparse
from multiprocessing import Process, Queue
import time

import ioutils
from googlengram.pullscripts.gramgrab import main

VERSION = '20120701'
TYPE = '5gram'
POS = re.compile('.*_[A-Z]+\s.*')
LINE_SPLIT = 100000000
EXCLUDE_PATTERN = re.compile('.*_[A-Z]+[_,\s].*')

def split_main(proc_num, queue, download_dir, out_dir_g, context_size):
    print proc_num, "Start loop"
    while True: # iterates throug the urls of the datafiles
        if queue.empty():
            break
        url = queue.get()
        name = re.search('%s-(.*).gz' % VERSION, url).group(1) # gets the name of the individual file
        dirs = set(os.listdir(download_dir))
        if name in [file.split("-")[0] for file in dirs]:
            continue

        print proc_num, "Name", name # creates the directiory for the downloading file
        loc_dir = download_dir + "/" + name + "/"
        ioutils.mkdir(loc_dir)

        print proc_num, "Downloading", name # downloads the actual compressed file
        success = False
        while not success:
            with open(loc_dir + name + '.gz', 'w') as f:
                try:
                    f.write(urllib2.urlopen(url, timeout=60).read())
                    success = True
                except:
                    print "Fail!!"
                    continue

        print proc_num, "Unzipping", name # Unzips and put the datafile into max LINE_SPLIT line long files
        subprocess.call(['gunzip', '-f', loc_dir + name + '.gz', '-d'])
        print proc_num, "Splitting", name
        subprocess.call(["split", "-l", str(LINE_SPLIT), loc_dir + name, download_dir + "/" +  name + "-"])
        os.remove(loc_dir + name)
        os.rmdir(loc_dir)

        # runs gramgrab
        print proc_num, "gram_grab", name
        queue_g = Queue()
        for item in os.listdir(download_dir + "/"):
            if name + "-" in item:
                queue_g.put(item)
        time.sleep(0.01)  # It is needed to eliminate unstability
        main(proc_num, queue_g, out_dir_g, download_dir, context_size)
        for item in os.listdir(download_dir + "/"):
            if name + "-" in item:
                os.remove(download_dir + "/" + item)

def run_parallel(num_processes, out_dir, source, context_size):
    page = requests.get("http://storage.googleapis.com/books/ngrams/books/datasetsv2.html") # gets the URL addresses from the code of the webpage of database
    pattern = re.compile('href=\'(.*%s-%s-%s-.*\.gz)' % (source, TYPE, VERSION))
    urls = pattern.findall(page.text)
    del page
    queue = Queue()
    for url in urls: # puts the urls into a queue
        queue.put(url)
    ioutils.mkdir(out_dir + '/' + source + '/raw')
    download_dir = out_dir + '/' + source + '/raw/'
    out_dir_g = out_dir + '/' + source + '/c' + str(context_size) + '/raw/'
    ioutils.mkdir(download_dir)
    procs = [Process(target=split_main, args=[i, queue, download_dir, out_dir_g, context_size]) for i in range(num_processes)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", help="directory where data will be stored")
    parser.add_argument("source", help="source dataset to pull from (must be available on the N-Grams website")
    parser.add_argument("context_size", type=int, help="Size of context window. Currently only size 2 and 4 are supported.")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    args = parser.parse_args()
    run_parallel(args.num_procs, args.out_dir, args.source, args.context_size) 