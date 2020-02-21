# Modification of seq_procrustes.py for the cloud modell: Rotates the embeddings of individual years to each other, then the avarage embeddings to the previous year.
# e.g. python -m vecanalysis.seq_procrustes_clouds data_dir sgns 80 data_dir/common_vocab.pkl

import numpy as np
from argparse import ArgumentParser

from vecanalysis import alignment
from representations.representation_factory import create_representation
from representations.embedding import Embedding
from ioutils import load_pickle, write_pickle, words_above_count, mkdir

def align_years(years, rep_type, main_dir, num, dim, **rep_args):
    print "Aligning years to each other"
    first_iter = True
    base_embed = None
    for year in years: # Iterates through years
        print year
        year_embed =  create_representation(rep_type, main_dir + "/embedding_avg/" + str(year), **rep_args) # Loads the individual embedding
        if first_iter:
            aligned_embed = year_embed
            first_iter = False
        else:
            ortho = alignment.get_procrustes_mat(base_embed, year_embed)
            aligned_embed = Embedding((year_embed.m).dot(ortho), year_embed.iw, normalize=False) # Rotates to the previous year embedding
            for i in range(1, num + 1): # Align all the embedding the same way as the avarage
                finname = main_dir + "/embedding_" + str(i) + "/noinit/" + str(dim) + "/aligned/" + str(year)
                foutname = main_dir + "/embedding_" + str(i) + "/noinit/" + str(dim) + "/aligned/" + str(year)
                mat = np.load(finname + "-w.npy")
                mat = mat.dot(ortho)
                np.save(foutname + "-w.npy", mat)
        base_embed = aligned_embed
        foutname = main_dir + "/embedding_avg/aligned/" + str(year)
        np.save(foutname + "-w.npy", aligned_embed.m)
        write_pickle(aligned_embed.iw, foutname + "-vocab.pkl")

def align_cloud(year, rep_type, main_dir, num, dim, wordlist, **rep_args):
    print "Aligning cloud year:", year
    avg_embed_mat = np.zeros((len(wordlist), dim))
    for i in range(1, num + 1): # Iterates throug the embeddings
        print i
        finname = main_dir + "/embedding_" + str(i) + "/noinit/" + str(dim) + "/" + str(year)
        foutname = main_dir + "/embedding_" + str(i) + "/noinit/" + str(dim) + "/aligned/" + str(year)
        other_embed =  create_representation(rep_type, finname, **rep_args) # Loads the individual embedding
        keep_indices = [other_embed.wi[word] for word in wordlist]
        other_embed = Embedding(other_embed.m[keep_indices, :], wordlist, normalize=False) # Synchronize the order of words
        if i == 1:
            base_embed = other_embed
            ortho = np.eye(dim)
        else:
            ortho = alignment.get_procrustes_mat(base_embed, other_embed)
        aligned_embed_mat = (other_embed.m).dot(ortho) # Rotates the embedding to the reference
        avg_embed_mat += aligned_embed_mat / num # Creates avarage embedding
        np.save(foutname + "-w.npy", aligned_embed_mat)
        write_pickle(other_embed.iw, foutname + "-vocab.pkl")
    foutname = main_dir + "/embedding_avg/" + str(year)
    np.save(foutname + "-w.npy", avg_embed_mat)
    write_pickle(base_embed.iw, foutname + "-vocab.pkl")
        

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("dir")
    parser.add_argument("rep_type")
    parser.add_argument("num_emb", help="number of different embedding-series", type=int)
    parser.add_argument("wordlist")
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    parser.add_argument("--year-inc", type=int, default=1)
    parser.add_argument("--dim", type=int, default=300)
    args = parser.parse_args()
    kwargs = dict()
    if (args.rep_type.lower() == "sgns"):
        kwargs["normalize"] = False
    wordlist = load_pickle(args.wordlist)
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    mkdir(args.dir + "/embedding_avg/")
    mkdir(args.dir + "/embedding_avg/aligned")
    for i in range(1, args.num_emb + 1):
        mkdir(args.dir + "/embedding_" + str(i) + "/noinit/" + str(args.dim) + "/aligned/")
    for year in years:
        align_cloud(year, args.rep_type, args.dir, args.num_emb, args.dim, wordlist, **kwargs)
    align_years(years, args.rep_type, args.dir, args.num_emb, args.dim, **kwargs)
