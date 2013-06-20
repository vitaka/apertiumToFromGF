# ! /bin/bash
CURDIR=`dirname $0`
PYDIR=$CURDIR/src/py


#shflags
. $CURDIR/shflags
DEFINE_string 'abstract_gf' '' 'Abstract syntax generated from Apertium' 's'
DEFINE_string 'abstract_gf_dict' '' 'Abstract syntax of words from GF' 'd'
DEFINE_string 'probabilities_file' '' 'Original probabilities file' 'p'
DEFINE_float 'alpha_known' '0.9' '' 'a'
DEFINE_boolean 'keep_tmp_dir' 'false' 'do not remove temporal dir' 'k'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"


TMPDIR=`mktemp -d`

echo "TMPDIR: $TMPDIR" 1>&2

cat ${FLAGS_abstract_gf} | cut -f 1 -d ':' | sed 's_ *$__' | grep -v "{" | grep -v "}" | grep -v '^fun$' > $TMPDIR/abstractwords
cat $TMPDIR/abstractwords | sed 's:^.*_::' | LC_ALL=C sort | uniq > $TMPDIR/abstractcats
cat ${FLAGS_abstract_gf_dict} | sed 's_}$_\n}_' | cut -f 2 -d ' ' | sed 's_ *$__' | grep -v "{" | grep -v "}"  >> $TMPDIR/abstractwords

ORIGINAPROBS=${FLAGS_probabilities_file}

GREPSTRING=""
for c in `cat $TMPDIR/abstractcats` ; do
	GREPSTRING="$GREPSTRING\|_$c	"

	cat $ORIGINAPROBS | grep "_$c	" > $TMPDIR/originalprobs$c
	cat $TMPDIR/abstractwords  | grep "_$c\$" > $TMPDIR/abstractwordsfrom$c
	
	touch $TMPDIR/result-denormalized-$c
	touch $TMPDIR/result-unknown-$c
	
	for word in `cat $TMPDIR/abstractwordsfrom$c`; do
		FOUND=`cat $TMPDIR/originalprobs$c | grep "^$word	"`
		if [ "$FOUND" != "" ]; then
			echo "$FOUND" >> $TMPDIR/result-denormalized-$c 
		else
			echo "$word" >> $TMPDIR/result-unknown-$c
		fi
	done
	
	ALPHAFORKNOWN=${FLAGS_alpha_known}
	
	#unknown words have the same probability
	NUM_UNKNOWN=`cat $TMPDIR/result-unknown-$c | wc -l`
	
	if [ "$NUM_UNKNOWN" != "0" ]; then
		UNKNOWN_PROB=`echo "(1.0 - $ALPHAFORKNOWN ) / $NUM_UNKNOWN " | python -c "import sys;[ sys.stdout.write('{0:0.16e}'.format(eval(line))+'\\n') for line in sys.stdin ]"`
		cat $TMPDIR/result-unknown-$c | sed "s:\$:	$UNKNOWN_PROB:" > $TMPDIR/result-unknown-with-probs-$c
	else
		touch $TMPDIR/result-unknown-with-probs-$c
		ALPHAFORKNOWN="1.0"
	fi
	
	#normalise probabilities of known words and multiply them by alpha_known
	TOTAL_PROB=`cat $TMPDIR/result-denormalized-$c | cut -f 2 | python $PYDIR/sumFloating.py`
	cat $TMPDIR/result-denormalized-$c | cut -f 2 | sed "s:\$: * $ALPHAFORKNOWN / $TOTAL_PROB:" | python -c "import sys;[ sys.stdout.write('{0:0.16e}'.format(eval(line))+'\\n') for line in sys.stdin ]" > $TMPDIR/normalized-probs-$c
	cat $TMPDIR/result-denormalized-$c | cut -f 1 | paste - $TMPDIR/normalized-probs-$c > $TMPDIR/result-known-with-probs-$c
done

# print probabilities of the original file not covering categories imported from Apertium
GREPSTRINGB=`echo "$GREPSTRING" | sed 's/^..//'`
cat $ORIGINAPROBS | grep -v "$GREPSTRINGB"

#now print probabilities of all the Apertium categories (and words from the Apertium categories not imported from Apertium, e.g., do_V2)
for c in `cat $TMPDIR/abstractcats` ; do
	cat $TMPDIR/result-known-with-probs-$c $TMPDIR/result-unknown-with-probs-$c
done



#remove tmp dir
if [ "${FLAGS_keep_tmp_dir}" == "${FLAGS_FALSE}" ]; then
	rm -Rf $TMPDIR
fi
