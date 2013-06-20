#! /bin/bash

# Computes some statistics about the parsing performance 
# Takes as an input the directory created by learnAbstractSyntax.sh
#

CURDIR=`dirname $0`
PYDIR=$CURDIR/src/py

#shflags
. $CURDIR/shflags
DEFINE_string 'trees_clean' '' 'trees clean file' 'f'
DEFINE_string 'sentences' '' 'sentences file' 'n'
DEFINE_string 'source_language' '' 'source language' 's'
DEFINE_string 'target_language' '' 'target language' 't'
DEFINE_string 'source_pgf' '' 'source language PGF' 'o'
DEFINE_string 'target_pgf' '' 'target language PGF' 'a'
DEFINE_string 'tmp_dir' '' 'temporary directory' 'm'
DEFINE_boolean 'keep_tmp_dir' 'false' 'do not remove temporal directory' 'k'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"


if [ "${FLAGS_tmp_dir}" == "" ]; then
	TMPDIR=`mktemp -d`
else
	TMPDIR=${FLAGS_tmp_dir}
	mkdir -p $TMPDIR
fi

echo "Temporary directory: $TMPDIR" 1>&2

paste -d '~' ${FLAGS_trees_clean}.sl ${FLAGS_trees_clean}.tl | LD_LIBRARY_PATH=/home/vmsanchez/estancia/local/lib/ PYTHONPATH=/home/vmsanchez/estancia/local/lib/python2.7/site-packages/ python $PYDIR/extractParallelTrees.py --source_pgf ${FLAGS_source_pgf} --target_pgf ${FLAGS_target_pgf} --only_count_parsed_words 2> $TMPDIR/parallelTreesWithBilingualPhrases.debug | gzip > $TMPDIR/parsedwords.gz

zcat $TMPDIR/parsedwords.gz | cut -f 1 -d '|' > $TMPDIR/parsedwords.sl
zcat $TMPDIR/parsedwords.gz | cut -f 2 -d '|' > $TMPDIR/parsedwords.tl

#rm -f $TMPDIR/propparsed.sl
#rm -f $TMPDIR/propparsed.tl

SUM_WORDS_SL=0
SUM_PARSED_WORDS_SL=0
paste -d '|' ${FLAGS_sentences}.${FLAGS_source_language} $TMPDIR/parsedwords.sl > $TMPDIR/sentencesplusparsed.sl
while read line ; do
	TOTAL_WORDS=`echo "$line" | cut -f 1 -d '|' | wc -w`
	PARSED_WORDS=`echo "$line" | cut -f 2 -d '|' | wc -w`
	#echo "$PARSED_WORDS / $TOTAL_WORDS" | bc -l >> $TMPDIR/propparsed.sl
	SUM_WORDS_SL=`expr $SUM_WORDS_SL + $TOTAL_WORDS`
	SUM_PARSED_WORDS_SL=`expr $SUM_PARSED_WORDS_SL + $PARSED_WORDS`
done < $TMPDIR/sentencesplusparsed.sl

SUM_WORDS_TL=0
SUM_PARSED_WORDS_TL=0
paste -d '|' ${FLAGS_sentences}.${FLAGS_target_language} $TMPDIR/parsedwords.tl > $TMPDIR/sentencesplusparsed.tl
while read line ; do
	TOTAL_WORDS=`echo "$line" | cut -f 1 -d '|' | wc -w`
	PARSED_WORDS=`echo "$line" | cut -f 2 -d '|' | wc -w`
	#echo "$PARSED_WORDS / $TOTAL_WORDS" | bc -l >> $TMPDIR/propparsed.tl
	SUM_WORDS_TL=`expr $SUM_WORDS_TL + $TOTAL_WORDS`
	SUM_PARSED_WORDS_TL=`expr $SUM_PARSED_WORDS_TL + $PARSED_WORDS`
done < $TMPDIR/sentencesplusparsed.tl

echo "Proportion parsed words SL ($SUM_PARSED_WORDS_SL / $SUM_WORDS_SL) : "
echo "$SUM_PARSED_WORDS_SL / $SUM_WORDS_SL" | bc -l

echo "Proportion parsed words TL ($SUM_PARSED_WORDS_TL / $SUM_WORDS_TL): "
echo "$SUM_PARSED_WORDS_TL / $SUM_WORDS_TL" | bc -l



#remove tmp dir
if [ "${FLAGS_keep_tmp_dir}" == "${FLAGS_FALSE}" -a "${FLAGS_tmp_dir}" == "" ]; then
	rm -Rf $TMPDIR
fi