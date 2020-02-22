# Downloads the 1gram datas and creates pkl files about word frequency statistics
# e.g. python -m googlengram.pullscripts.posgrab counts http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-fiction-all --start-year 1800 --end-year 2000
# Modified by Bogdan Asztalos
# MAY BE UNSTABLE

import requests
import urllib2
import re
import os
import subprocess
import argparse
import collections

from nltk.stem import snowball

import ioutils

VERSION = '20120701'
TYPE = '1gram'
POS = re.compile('[^_]+_[A-Z]+')

def main(out_dir, source, years):
    page = requests.get("http://storage.googleapis.com/books/ngrams/books/datasetsv2.html") # gets the urls of the 1gram datafiles
    pattern = re.compile('href=\'(.*%s-%s-%s-.*\.gz)' % (source, TYPE, VERSION))
    urls = pattern.findall(page.text)
    del page

    year_counts = {} # These are dicts that contain the occurence of a word in each year
    year_doc_counts = {}
    year_pos = {}
    for year in years:
        year_pos[year] = {} # Counts the occurrence of a word (distinguish words by pos)
        year_counts[year] = {} # Counts the occurrence of a word (does not distinguish words by pos)
        year_doc_counts[year] = {} # Counts the books where the word occurred

    print "Start loop"
    for url in urls: # iterates through the urls
        name = re.search('%s-(.*).gz' % VERSION, url).group(1)
        print  "Downloading", name

        success = False
        while not success: # downloads the acutal datafile
            with open(out_dir + name + '.gz', 'w') as f:
                try:
                    f.write(urllib2.urlopen(url, timeout=60).read())
                    success = True
                except:
                    continue

        print  "Unzipping", name # unzips the downloaded datafile
        subprocess.call(['gunzip', '-f', out_dir + name + '.gz', '-d'])

        print  "Going through", name # iterates through the lines of the datafile and counts the uccurrence of the words
        with open(out_dir + name) as f:
            for l in f: 
                try:
                    split = l.strip().split('\t')
                    if not POS.match(split[0]):
                        continue
                    count = int(split[2])
                    if count < 10:
                        continue
                    word_info = split[0].split("_") 
                    pos = word_info[-1]
                    word = word_info[0].decode('utf-8').lower()
                    word = word.strip("\"")
                    word = word.split("\'s")[0]
                    if not word.isalpha():
                        continue
                    esb = snowball.EnglishStemmer()
                    word = str(esb.stem(word))
                    year = int(split[1])
                    doc_count = int(split[3])
                    if not year in years:
                        continue
                    if not word in year_counts[year]:
                        year_counts[year][word] = 0
                        year_doc_counts[year][word] = 0
                        year_pos[year][word] = collections.Counter() 
                    year_counts[year][word] += count 
                    year_doc_counts[year][word] += doc_count 
                    year_pos[year][word][pos] += count
                except UnicodeDecodeError:
                     pass

        print "Deleting", name # deletes the downloaded files
        try:
            os.remove(out_dir + name)
            os.remove(out_dir + name + '.gz')
        except:
            pass

    print "Writing..." # writes the data into pkl files
    for year in years:
        ioutils.write_pickle(year_counts[year], out_dir + str(year) + "-counts.pkl")
        ioutils.write_pickle(year_doc_counts[year], out_dir + str(year) + "-doc_counts.pkl")
        ioutils.write_pickle(year_pos[year], out_dir + str(year) + "-pos.pkl")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pulls and saves unigram data.")
    parser.add_argument("out_dir", help="directory where data will be stored")
    parser.add_argument("source", help="source dataset to pull from (must be available on the N-Grams website")
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1)
    ioutils.mkdir(args.out_dir)
    main(args.out_dir + "/", args.source, years) 
