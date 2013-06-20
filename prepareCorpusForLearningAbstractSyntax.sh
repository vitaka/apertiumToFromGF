#! /bin/bash

CURDIR=`dirname $0`
SCRIPTSDIR="$CURDIR/src/scripts"

###########################################
# Prepares a corpus to learn multi-word expressions from it
# This script tokenizes both sides of the corpus, removes long and single-word sentences, and lines containing
# more than one sentence
################################################

#shflags
. $CURDIR/shflags

######################
# (compulsory)
# Extension of the source language corpus files
######################
DEFINE_string 'source_language' '' 'source language' 's'

######################
# (compulsory)
# Extension of the target language corpus files
######################
DEFINE_string 'target_language' '' 'target language' 't'

#####################
# (compulsory)
# Name of the files containing the input parallel corpus
# The extensions of such files are defined with the source_language and target_language parameters
# That is, the program will read the files $input_corpus.$source_language and $input_corpus.$target_language
# 
######################
DEFINE_string 'input_corpus' '' 'corpus file prefix' 'c'

#####################
# (compulsory)
# Name of the files which will contain the prepared parallel corpus
# The extensions of such files are defined with the source_language and target_language parameters
# That is, the program will create the files $output_corpus.$source_language and $input_corpus.$target_language
# 
######################
DEFINE_string 'output_corpus' '' 'corpus file prefix' 'o'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

TMPDIR=`mktemp -d`
echo "Temporary directory: $TMPDIR" 1>&2

SL=${FLAGS_source_language}
TL=${FLAGS_target_language}

SLFILE=${FLAGS_input_corpus}.${FLAGS_source_language}
TLFILE=${FLAGS_input_corpus}.${FLAGS_target_language}

OUTPUTSLFILE=${FLAGS_output_corpus}.${FLAGS_source_language}
OUTPUTTLFILE=${FLAGS_output_corpus}.${FLAGS_target_language}

#normalize punctuation and tokenize
cat $SLFILE | perl $SCRIPTSDIR/normalize-punctuation.perl $SL |  perl $SCRIPTSDIR/tokenizer.perl -l $SL > $TMPDIR/tok.$SL
cat $TLFILE | perl $SCRIPTSDIR/normalize-punctuation.perl $TL |  perl $SCRIPTSDIR/tokenizer.perl -l $TL > $TMPDIR/tok.$TL

#remove long and single-word sentences
perl $SCRIPTSDIR/clean-corpus-n.perl $TMPDIR/tok  $SL $TL $TMPDIR/tok.short 2 26

#remove lines which contain more than one sentence
paste -d '|' $TMPDIR/tok.short.$SL $TMPDIR/tok.short.$TL | grep -E '^[^?!.]*[?!.]?\|[^?!.]*[?!.]?$' | cut -f 1 -d '|' > $OUTPUTSLFILE
paste -d '|' $TMPDIR/tok.short.$SL $TMPDIR/tok.short.$TL | grep -E '^[^?!.]*[?!.]?\|[^?!.]*[?!.]?$' | cut -f 2 -d '|' > $OUTPUTTLFILE

rm -Rf $TMPDIR