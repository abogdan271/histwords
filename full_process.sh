#!/bin/bash
# This scripts executes all the programmes for a diachronic embedding with the cloud model
set -e

# Download and process the n-gram data
python -m googlengram.pullscripts.downloadandsplit_gramgrab data_dir/ http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-fiction-all 2 5
mv data_dir/http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-fiction-all data_dir/unmerged
python -m googlengram.pullscripts.runmerge data_dir/merged/ data_dir/unmerged/c2/raw/ 5 --start-year 1950 --end-year 1999 --year-inc 1

# Merge data and create the co-occurrence matrix
python -m googlengram.pullscripts.indexmerge data_dir/index_merged/ data_dir/merged/ english --start-year 1950 --end-year 1999 --year-inc 1
python -m googlengram.pullscripts.countmerge data_dir/index_merged/ data_dir/merged/ 5 --start-year 1950 --end-year 1999 --year-inc 1
python -m googlengram.makedecades data_dir/decades/ data_dir/index_merged/ 5 --start-year 1950 --end-year 1990 --year-inc 1
python -m googlengram.makecounts data_dir/counts/ data_dir/decades/ 5 2 --start-year 1950 --end-year 1990
python -m googlengram.makecommonvocab data_dir/decades/ data_dir/decades/ data_dir/counts/ --start-year 1950 --end-year 1990 --year-inc 1

# Create the embeddings
mkdir data_dir/embeddings
for i in {1..80}
do
    echo Embedding $i
    mkdir data_dir/embeddings/embedding_$i
    python -m sgns.makecorpus_variants.makecorpus_eq data_dir/embeddings/corpus/ data_dir/decades/ data_dir/counts/ data_dir/decades/common_vocab.pkl --workers 5 --start-year 1950 --end-year 1990
    python -m sgns.runword2vec data_dir/embeddings/corpus/ data_dir/embeddings/embedding_$i/ --workers 5 --start-year 1950 --end-year 1990
    python -m sgns.postprocesssgns data_dir/embeddings/embedding_$i/noinit/300/ --workers 5 --start-year 1950 --end-year 1990
    python -m sgns.rm_trash data_dir/embeddings/embedding_$i/noinit/300/ --workers 5 --start-year 1950 --end-year 1990
done
rm -r data_dir/embeddings/corpus/

# Do Procrustes algorithm
python -m vecanalysis.seq_procrustes_clouds data_dir/embeddings/ sgns 80 data_dir/decades/common_vocab.pkl --start-year 1950 --end-year 1990
