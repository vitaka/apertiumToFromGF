#! /bin/bash

CURDIR=`dirname $0`
PYDIR=$CURDIR/src/py

###########################################
# Extracts parallel trees representing multi-word expressions with variables from
# a parallel corpus.
#
# Results are found in $TMPDIR (see parameters below)
#   - finalmwes-$THRESHOLD.gz contains MWES with gaps
#   - finalmwes-no-wildcards-$THRESHOLD.gz contains MWES without gaps
################################################

#Values for LD_LIBRARY_PATH and PYTHON_PATH. Change them accordingly
VAR_LD_LIBRARY_PATH=/home/vmsanchez/estancia/local/lib/
VAR_PYTHON_PATH=/home/vmsanchez/estancia/local/lib/python2.7/site-packages/

function files_exist ()
{
	for var in "$@" ;
	do
		if [ ! -f "$var" ]; then
			return 1
		fi
	done
	return 0
}

#shflags
. $CURDIR/shflags
#####################
# (compulsory)
# Name of the files containing the trees obtained after parsing each side of the parallel corpus
# The extensions of such files are defined with the source_language and target_language parameters
# That is, the program will read the files $trees_file.$source_language and $trees_file.$target_language
# Parsing must be performed with the script robustTranslationGF.sh and the option --output_is_tree_raw
# 
######################
DEFINE_string 'trees_file' '' 'files containing trees' 'f'

######################
# (compulsory)
# Extension of the source language trees file
######################
DEFINE_string 'source_language' '' 'source language' 's'

######################
# (compulsory)
# Extension of the target language trees file
######################
DEFINE_string 'target_language' '' 'target language' 't'

######################
# (compulsory)
# Source language PGF file
######################
DEFINE_string 'source_pgf' '' 'source language PGF' 'o'

######################
# (compulsory)
# Target language PGF file
######################
DEFINE_string 'target_pgf' '' 'target language PGF' 'a'

######################
# (compulsory)
# File containing the bilingual phrases and alignments extracted from the parallel corpus.
# It must be obtained with the script alignParallelCorpus.sh
######################
DEFINE_string 'learn_mwe_with_alignments' '' 'bilingual phrases extracted by moses from the parallel corpus' 'b'

######################
# (optional)
# Temporary directory where all the the files will be stored
# If not set, the script will create a new temporary directory under /tmp
######################
DEFINE_string 'tmp_dir' '' 'temporary directory' 'm'

######################
# (optional, flag)
# Activate this flag to avoid automatically removing the temporary directory after computing the multi-word expressions
######################
DEFINE_boolean 'keep_tmp_dir' 'false' 'do not remove temporal directory' 'k'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

SL=${FLAGS_source_language}
TL=${FLAGS_target_language}
INPUTFILE=${FLAGS_trees_file}

if [ "${FLAGS_tmp_dir}" == "" ]; then
	TMPDIR=`mktemp -d`
else
	TMPDIR=${FLAGS_tmp_dir}
	mkdir -p $TMPDIR
fi

echo "Temporary directory: $TMPDIR" 1>&2

#Clean output of GF robust parser
OUTPUT="$TMPDIR/trees.clean.sl $TMPDIR/trees.clean.tl"
files_exist $OUTPUT
if [ $? != 0 ]; then
	#clean raw data
	cat $INPUTFILE.$SL | grep "\[[0-9\.]*\]" | sed 's_[^]]*\] __' | grep -v '"SYMBOLTHISISADOT"\|"ENDOFLINE"\|"SYMBOLINTERROGATIONMARK"\|"SYMBOLEXCLAMATIONMARK"' > $TMPDIR/trees.clean.sl

	cat $INPUTFILE.$TL | grep "\[[0-9\.]*\]" | sed 's_[^]]*\] __' | grep -v '"SYMBOLTHISISADOT"\|"ENDOFLINE"\|"SYMBOLINTERROGATIONMARK"\|"SYMBOLEXCLAMATIONMARK"' > $TMPDIR/trees.clean.tl
fi

if [ "${FLAGS_learn_mwe_with_alignments}" != "" ] ; then
	
	OUTPUT=$TMPDIR/bilingualPhrases
	files_exist $OUTPUT
	if [ $? != 0 ]; then
		NUMLINESTREES=`cat $TMPDIR/trees.clean.sl | wc -l`
		#group bilinual phrases in the same line
		cat ${FLAGS_learn_mwe_with_alignments} | tr '\n' '\t' | sed 's:\tENDOFLINE ||| ENDOFLINE ||| 0-0:\n:g' | sed 's:^\t::' | head -n $NUMLINESTREES > $OUTPUT
	fi
	
	#Extract parallel trees
	OUTPUT=$TMPDIR/parallelTreesWithBilingualPhrasesLexicalised.gz
	files_exist $OUTPUT
	if [ $? != 0 ]; then
		paste -d '~' $TMPDIR/trees.clean.sl $TMPDIR/trees.clean.tl $TMPDIR/bilingualPhrases | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/extractParallelTrees.py --source_pgf ${FLAGS_source_pgf} --target_pgf ${FLAGS_target_pgf} --with_bilingual_phrases  --create_bilingual_dictionary $TMPDIR/bilingualDictionary 2> $TMPDIR/parallelTreesWithBilingualPhrases.debug | gzip > $OUTPUT
	fi
	
	
	OUTPUT="$TMPDIR/candidatemwes.gz $TMPDIR/candidatemwes-inv.gz"
	files_exist $OUTPUT
	if [ $? != 0 ]; then
		#remove context
		zcat $TMPDIR/parallelTreesWithBilingualPhrasesLexicalised.gz | cut -f 2,4 -d '|' | sed 's:^ *::' | gzip > $TMPDIR/parallelTreesWithBilingualPhrasesLexicalisedNoContext.gz
		
		#count
		zcat $TMPDIR/parallelTreesWithBilingualPhrasesLexicalisedNoContext.gz | LC_ALL=C sort | uniq -c |  sed 's:^ *::' | sed 's: : | :' | gzip > $TMPDIR/pairs.gz
		
		#extract candidate MWEs
		zcat $TMPDIR/pairs.gz | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/extractCandidateMWEs.py --use_synonyms $TMPDIR/bilingualDictionary | LC_ALL=C sort | uniq |  gzip > $TMPDIR/candidatemwes-withrepresentatives.gz
		
		#remove representative and and re-sort if necessary
		zcat $TMPDIR/candidatemwes-withrepresentatives.gz | awk -F"|" '{print $3 "|" $4}' | sed 's:^ *::' | gzip > $TMPDIR/candidatemwes.gz
		zcat $TMPDIR/candidatemwes-withrepresentatives.gz | awk -F"|" '{print $2 "|" $4 "|" $3 }' | sed 's:\([^ ]\)|:\1 |:' |  sed 's:^ *::' | sed 's: *$::' | LC_ALL=C sort | awk -F"|" '{print $2 "|" $3}' | sed 's:^ *::' | gzip > $TMPDIR/candidatemwes-inv.gz
	fi
	
	OUTPUT="$TMPDIR/mwes-dir.gz $TMPDIR/mwes-inv.gz"
	files_exist $OUTPUT
	if [ $? != 0 ]; then

		#invert pairs
		zcat $TMPDIR/pairs.gz | awk -F"|" '{print $1 "|" $3 "|" $2}' |  sed 's:\([^ ]\)|:\1 |:' | gzip > $TMPDIR/pairs-inv.gz
		
		rm -Rf $TMPDIR/candidates
		rm -Rf $TMPDIR/candidates-inv
		
		mkdir -p $TMPDIR/candidates
		mkdir -p $TMPDIR/candidates-inv
		
		zcat $TMPDIR/candidatemwes.gz | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/splitCandidateMWEsinGroups.py --groups_dir $TMPDIR/candidates
		zcat $TMPDIR/candidatemwes-inv.gz | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/splitCandidateMWEsinGroups.py --groups_dir $TMPDIR/candidates-inv
		
		
		#select MWEs in parallel
		find $TMPDIR/candidates/  -not -type d > $TMPDIR/candidates-list
		find $TMPDIR/candidates-inv/  -not -type d > $TMPDIR/candidates-inv-list
		
		parallel -i bash -c "cat {} | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/selectMWEs.py --bilingual_exprs $TMPDIR/pairs.gz --use_synonyms $TMPDIR/bilingualDictionary --debug 2> {}.debug  | gzip > {}.result.gz" -- `cat $TMPDIR/candidates-list` &
		PID1=$!
		
		parallel -i bash -c "cat {} | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/selectMWEs.py --bilingual_exprs $TMPDIR/pairs-inv.gz --use_synonyms $TMPDIR/bilingualDictionary.inv --debug 2> {}.debug  | gzip > {}.result.gz" -- `cat $TMPDIR/candidates-inv-list` &
		PID2=$!
		
		wait $PID1 $PID2
		
		#reduce parallel results
		rm -f $TMPDIR/mwes-dir $TMPDIR/mwes-dir.gz
		for FPREFIX in `cat $TMPDIR/candidates-list`; do
			zcat ${FPREFIX}.result.gz >> $TMPDIR/mwes-dir
		done
		gzip $TMPDIR/mwes-dir
		
		#reduce parallel results
		rm -f $TMPDIR/mwes-inv $TMPDIR/mwes-inv.gz
		for FPREFIX in `cat $TMPDIR/candidates-inv-list`; do
			zcat ${FPREFIX}.result.gz >> $TMPDIR/mwes-inv
		done
		gzip $TMPDIR/mwes-inv
	fi
	
	OUTPUT="$TMPDIR/mwes-structural-and-lowprobincluded.gz"
	files_exist $OUTPUT
	if [ $? != 0 ]; then
		zcat $TMPDIR/mwes-dir.gz | python $PYDIR/filterMWEsByProp.py --min_prop_reproduced 0.0 | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/filterFinalMWEs.py   --different_sides > $TMPDIR/mwes-structural-and-lowprobincluded
		gzip $TMPDIR/mwes-structural-and-lowprobincluded
	fi
	
	for THRESHOLD in 0.51 `LC_ALL=C seq 0.55 0.05 0.95` ; do
		OUTPUT="$TMPDIR/mwes-dir-filtered-$THRESHOLD.gz $TMPDIR/mwes-inv-filtered-$THRESHOLD.gz"
		files_exist $OUTPUT
		if [ $? != 0 ]; then
			#filter results
			zcat $TMPDIR/mwes-dir.gz | python $PYDIR/filterMWEsByProp.py --min_prop_reproduced $THRESHOLD | gzip > $TMPDIR/mwes-dir-filtered-$THRESHOLD.gz
			zcat $TMPDIR/mwes-inv.gz | python $PYDIR/filterMWEsByProp.py --min_prop_reproduced $THRESHOLD | gzip > $TMPDIR/mwes-inv-filtered-$THRESHOLD.gz
		fi
		
		
		OUTPUT="$TMPDIR/finalmwes-$THRESHOLD.gz $TMPDIR/finalmwes-no-wildcards-$THRESHOLD.gz"
		files_exist $OUTPUT
		if [ $? != 0 ]; then
			#choose intersection
			zcat  $TMPDIR/mwes-dir-filtered-$THRESHOLD.gz | LC_ALL=C sort >  $TMPDIR/mwes-dir-sorted-$THRESHOLD
			zcat  $TMPDIR/mwes-inv-filtered-$THRESHOLD.gz | awk -F"|" '{print $2 "|" $1}' | sed 's:^ *::' | sed 's: *$::' | sed 's:|: | :' | LC_ALL=C sort > $TMPDIR/mwes-inv-sorted-$THRESHOLD
			LC_ALL=C comm -12 $TMPDIR/mwes-dir-sorted-$THRESHOLD $TMPDIR/mwes-inv-sorted-$THRESHOLD | gzip > $TMPDIR/mwes-$THRESHOLD.gz
			
			#filter mwes: first remove compositionally equivalent
			zcat $TMPDIR/mwes-$THRESHOLD.gz | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/addCompositionallyEquivalentRefsMWEs.py --use_synonyms $TMPDIR/bilingualDictionary --additional_references $TMPDIR/mwes-structural-and-lowprobincluded.gz | gzip > $TMPDIR/mwescomp-$THRESHOLD.gz
			
			#finally, remove those without lexical functions, without wildcards, or which are the same in both languages
			zcat $TMPDIR/mwescomp-$THRESHOLD.gz | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/filterFinalMWEs.py --different_sides --contains_non_wildcard --contains_wildcard | grep -v -F "othermwe" | gzip > $TMPDIR/finalmwes-$THRESHOLD.gz
			
			zcat $TMPDIR/mwescomp-$THRESHOLD.gz | LD_LIBRARY_PATH=$VAR_LD_LIBRARY_PATH PYTHONPATH=$VAR_PYTHON_PATH python $PYDIR/filterFinalMWEs.py --different_sides --not_contains_wildcard | grep -v -F "othermwe" | gzip > $TMPDIR/finalmwes-no-wildcards-$THRESHOLD.gz
		fi
	done
	
	zcat $TMPDIR/finalmwes-0.70.gz
else
	echo "ERROR: Parameter learn_mwe_with_alignments not set"
fi

#remove tmp dir
if [ "${FLAGS_keep_tmp_dir}" == "${FLAGS_FALSE}" -a "${FLAGS_tmp_dir}" == "" ]; then
	rm -Rf $TMPDIR
fi