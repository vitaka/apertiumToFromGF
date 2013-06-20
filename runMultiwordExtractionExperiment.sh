#! /bin/bash

# Script which extracts MWEs for different prefixes of a given corpus
# IMPORTANT: The corpus must be prepared first, with prepareCorpusForLearningAbstractSyntax.sh
# sizes is space-separated list of sizes, in increasing order. Each size must be a multiple of the first one
#


CURDIR=`dirname $0`

#shflags
. $CURDIR/shflags
DEFINE_string 'source_language' '' 'source language' 's'
DEFINE_string 'target_language' '' 'target language' 't'
DEFINE_string 'source_pgf' '' 'source language PGF file' 'o'
DEFINE_string 'target_pgf' '' 'target language PGF file' 'a'
DEFINE_string 'source_pgf_language' '' 'source language of PGF' 'u'
DEFINE_string 'target_pgf_language' '' 'target language of PGF' 'r'
DEFINE_string 'parallel_corpus' '' 'parallel corpus already prepared' 'c'
DEFINE_string 'sizes' '' 'subsets of the parallel corpus to test' 'n'
DEFINE_string 'dir' '' 'directory where all the stuff will be stored' 'd'
DEFINE_string 'first_step' '' 'directory where all the stuff will be stored' 'e'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

TMPDIR=`mktemp -d`
echo "Temporary directory: $TMPDIR" 1>&2

if [ "${FLAGS_first_step}" == "" ]; then
	FIRST_STEP=0
else
	FIRST_STEP=${FLAGS_first_step}
fi

SIZES=${FLAGS_sizes}
SIZES_ARRAY=( $SIZES )
FIRST_SIZE=${SIZES_ARRAY[0]}
LAST_INDEX=`expr ${#SIZES_ARRAY[@]}  - 1`
LAST_SIZE=${SIZES_ARRAY[$LAST_INDEX]}

SL=${FLAGS_source_language}
TL=${FLAGS_target_language}
CORPUS_FILE=${FLAGS_parallel_corpus}
CORPUS_NAME=`basename $CORPUS_FILE`

S_PGF_LANG=${FLAGS_source_pgf_language}
T_PGF_LANG=${FLAGS_target_pgf_language}

S_PGF_FILE=${FLAGS_source_pgf}
T_PGF_FILE=${FLAGS_target_pgf}



if [ "${FLAGS_dir}" == "" ]; then
	DIR=`dirname $CORPUS_FILE`
else
	DIR=${FLAGS_dir}
fi

#corpus must be already prepared

if [ 1 -ge "$FIRST_STEP" ]; then
	#split corpus in chunks of the smallest size
	cat ${CORPUS_FILE}.$SL | head -n $LAST_SIZE | split -l $FIRST_SIZE -d - $DIR/$CORPUS_NAME.split$FIRST_SIZE.$SL.
	cat ${CORPUS_FILE}.$TL | head -n $LAST_SIZE | split -l $FIRST_SIZE -d - $DIR/$CORPUS_NAME.split$FIRST_SIZE.$TL.

	#change names to make them more moses-friendly
	for f in `find $DIR -name "$CORPUS_NAME.split$FIRST_SIZE.$SL.*"`; do
		NUM=`echo "$f" | awk -F . '{print $NF}'`
		mv "$f" "$DIR/$CORPUS_NAME.split$FIRST_SIZE.$NUM.$SL"
	done

	for f in `find $DIR -name "$CORPUS_NAME.split$FIRST_SIZE.$TL.*"`; do
		NUM=`echo "$f" | awk -F . '{print $NF}'`
		mv "$f" "$DIR/$CORPUS_NAME.split$FIRST_SIZE.$NUM.$TL"
	done
fi


if [ 2 -ge "$FIRST_STEP" ]; then
	#parse the chunks in parallel
	parallel -j 6 -i bash -c "if [ ! -e $DIR/$CORPUS_NAME.split$FIRST_SIZE.{}.treesraw.$SL ]; then  cat $DIR/$CORPUS_NAME.split$FIRST_SIZE.{}.$SL | bash $CURDIR/robustTranslationGF.sh --source_language ${S_PGF_LANG} --source_pgf ${S_PGF_FILE} --output_is_tree_raw > $DIR/$CORPUS_NAME.split$FIRST_SIZE.{}.treesraw.$SL ; fi" -- ` find $DIR -name "$CORPUS_NAME.split$FIRST_SIZE.*.$SL" | awk -F '.' '{ print $(NF-1)}' `

	parallel -j 6 -i bash -c "if [ ! -e $DIR/$CORPUS_NAME.split$FIRST_SIZE.{}.treesraw.$TL ]; then cat $DIR/$CORPUS_NAME.split$FIRST_SIZE.{}.$TL | PATH=/home/vmsanchez/estancia/localfast/bin:\$PATH bash $CURDIR/robustTranslationGF.sh --source_language ${T_PGF_LANG} --source_pgf ${T_PGF_FILE} --output_is_tree_raw > $DIR/$CORPUS_NAME.split$FIRST_SIZE.{}.treesraw.$TL ; fi" -- ` find $DIR -name "$CORPUS_NAME.split$FIRST_SIZE.*.$TL" | awk -F '.' '{ print $(NF-1)}' `

	#join the chunks to fit the desired size
	for SIZE in $SIZES ; do
		
		if [ ! -e $DIR/$CORPUS_NAME.split$FIRST_SIZE.h$SIZE.treesraw.$SL -o ! -e $DIR/$CORPUS_NAME.split$FIRST_SIZE.h$SIZE.treesraw.$TL ]; then
		
		rm -f $DIR/$CORPUS_NAME.split$FIRST_SIZE.h$SIZE.treesraw.$SL
		rm -f $DIR/$CORPUS_NAME.split$FIRST_SIZE.h$SIZE.treesraw.$TL
		
		NUMCHUNKS=`expr $SIZE / $FIRST_SIZE`
		for CHUNKID in `find $DIR -name "$CORPUS_NAME.split$FIRST_SIZE.*.treesraw.$SL" | awk -F '.' '{ print $(NF-2)}' | LC_ALL=C sort | head -n $NUMCHUNKS`; do
			cat $DIR/$CORPUS_NAME.split$FIRST_SIZE.$CHUNKID.treesraw.$SL >> $DIR/$CORPUS_NAME.split$FIRST_SIZE.h$SIZE.treesraw.$SL
			cat $DIR/$CORPUS_NAME.split$FIRST_SIZE.$CHUNKID.treesraw.$TL >> $DIR/$CORPUS_NAME.split$FIRST_SIZE.h$SIZE.treesraw.$TL
		done
		
		fi
	done
fi


if [ 3 -ge "$FIRST_STEP" ]; then
	#Obtain alignments
	for SIZE in $SIZES ; do
		if [ ! -e $DIR/$CORPUS_NAME.h$SIZE.bilphrases ]; then
		
		cat $DIR/$CORPUS_NAME.$SL | head -n $SIZE > $DIR/$CORPUS_NAME.h$SIZE.$SL
		cat $DIR/$CORPUS_NAME.$TL | head -n $SIZE > $DIR/$CORPUS_NAME.h$SIZE.$TL
		bash $CURDIR/alignParallelCorpus.sh --source_language $SL --target_language $TL --corpus $DIR/$CORPUS_NAME.h$SIZE > $DIR/$CORPUS_NAME.h$SIZE.bilphrases
		
		fi
	done
fi

if [ 4 -ge "$FIRST_STEP" ]; then
	#extracts multiwords expressions. The directory is kept
	for SIZE in $SIZES ; do
		if [ ! -e $DIR/mwes-$CORPUS_NAME-h$SIZE ]; then
		
		bash $CURDIR/learnAbstractSyntax.sh --trees_file  $DIR/$CORPUS_NAME.split$FIRST_SIZE.h$SIZE.treesraw --source_language $SL --target_language $TL --source_pgf  $S_PGF_FILE --target_pgf $T_PGF_FILE --learn_mwe_with_alignments $DIR/$CORPUS_NAME.h$SIZE.bilphrases --tmp_dir $DIR/mwes-$CORPUS_NAME-h$SIZE --keep_tmp_dir
		
		fi
	done
fi
