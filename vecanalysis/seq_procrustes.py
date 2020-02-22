# Rotates embedding to each other
# e.g. python -m vecanalysis.seq_procrusetes data_dir sgns
# Modified by Bogdan Asztalos

import numpy as np
from argparse import ArgumentParser

from vecanalysis import alignment
from representations.representation_factory import create_representation
from ioutils import write_pickle, words_above_count, mkdir

def align_years(years, rep_type, in_dir, out_dir, **rep_args):
    first_iter = True
    base_embed = None
    for year in years: # Iterates through years
        print "Loading year:", year
        year_embed =  create_representation(rep_type, in_dir + str(year), **rep_args) # Loads the individual embedding
        print "Aligning year:", year
        if first_iter:
            aligned_embed = year_embed
            first_iter = False
        else:
            aligned_embed = alignment.smart_procrustes_align(base_embed, year_embed, post_normalize=False) # Rotates to the previous year embedding
        base_embed = aligned_embed
        print "Writing year:", year
        foutname = out_dir + str(year)
        np.save(foutname + "-w.npy",aligned_embed.m)
        write_pickle(aligned_embed.iw, foutname + "-vocab.pkl")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("dir")
    parser.add_argument("rep_type")
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    parser.add_argument("--year-inc", type=int, default=1)
    args = parser.parse_args()
    kwargs = dict()
    if (args.rep_type.lower() == "sgns"):
        kwargs["normalize"] = False
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    out_dir = args.dir + "/aligned/"
    mkdir(out_dir)
    align_years(years, args.rep_type, args.dir, out_dir, **kwargs)
