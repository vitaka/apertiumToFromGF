#! /bin/bash

CURDIR=`dirname $0`
PYDIR=$CURDIR/src/py

###############################################################
# Aligns a parallel corpus and extracts bilingual phrases using GIZA++ and Moses
# Only generates bilingual phrases with extremes aligned
# Output is stdout
################################################################

#shflags
. $CURDIR/shflags

######################
# (compulsory)
# Extension of the source language corpus file
######################
DEFINE_string 'source_language' '' 'source language' 's'

######################
# (compulsory)
# Extension of the target language corpus file
######################
DEFINE_string 'target_language' '' 'target language' 't'

######################
# (compulsory)
# Name of the parallel corpus files.
# The extensions of such files are defined with the source_language and target_language parameters
######################
DEFINE_string 'corpus' '' 'corpus file prefix' 'c'

######################
# (compulsory)
# Directory where the Moses scripts are installed
######################
DEFINE_string 'moses_scripts_dir' '/home/vmsanchez/wmt/tools/moses-scripts/' 'directory where the moses scripts are installed' 'm'

######################
# (optional, flag)
# Activate this flag to avoid automatically removing the temporary directory after aligning the corpus
######################
DEFINE_boolean 'keep_tmp_dir' 'false' 'do not remove temporal dir' 'k'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

CORPUS=${FLAGS_corpus}
SL=${FLAGS_source_language}
TL=${FLAGS_target_language}
MOSESSCRIPTSDIR=${FLAGS_moses_scripts_dir}

TMPDIR=`mktemp -d`
echo "Temporary directory: $TMPDIR" 1>&2

#get corpus
mkdir -p $TMPDIR/corpus
cp $CORPUS.$SL $TMPDIR/corpus/corpus.$SL 
cp $CORPUS.$TL $TMPDIR/corpus/corpus.$TL

#call moses
$MOSESSCRIPTSDIR/training/train-model.perl --last-step 3 --root-dir  $TMPDIR --corpus  $TMPDIR/corpus/corpus --f $SL --e $TL --parallel  --alignment grow-diag-final-and --max-phrase-length 40 2> $TMPDIR/moses1.err > $TMPDIR/moses1.out

#add special line marker to alignments and corpus files
cat $TMPDIR/model/aligned.grow-diag-final-and | sed 's:$:\n0-0:g' > $TMPDIR/model/aligned.mark.grow-diag-final-and
cat $TMPDIR/corpus/corpus.$SL | sed 's:$:\nENDOFLINE:g' > $TMPDIR/corpus/corpus.mark.$SL
cat $TMPDIR/corpus/corpus.$TL | sed 's:$:\nENDOFLINE:g' > $TMPDIR/corpus/corpus.mark.$TL

$MOSESSCRIPTSDIR/training/train-model.perl --first-step 4 --last-step 5 --root-dir  $TMPDIR --corpus  $TMPDIR/corpus/corpus.mark --f $SL --e $TL --parallel --alignment grow-diag-final-and --alignment-file $TMPDIR/model/aligned.mark --max-phrase-length 40 2> $TMPDIR/moses2.err > $TMPDIR/moses2.out

#output biligual phrases and remove those in which extremes are not aligned
zcat $TMPDIR/model/extract.gz | python $PYDIR/selectBilingualPhrasesWithExtremesAligned.py

#remove tmp dir
if [ "${FLAGS_keep_tmp_dir}" == "${FLAGS_FALSE}" ]; then
	rm -Rf $TMPDIR
fi
