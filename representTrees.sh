#! /bin/bash

# processes the raw output of pgf-translate (stdin) and 
# creates a tree representation in .eps format for each line
# of the output. 

CURDIR=`dirname $0`
PYDIR=$CURDIR/src/py

#shflags
. $CURDIR/shflags
DEFINE_string 'dir' '~/trees' 'directory where the trees will be stored' 'd'
DEFINE_string 'pgf' '' 'pgf file' 'p'
DEFINE_boolean 'keep_tmp_dir' 'false' 'do not remove temporal dir' 'k'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

DIR=${FLAGS_dir}
PGF=${FLAGS_pgf}

mkdir -p $DIR

TMPDIR=`mktemp -d`
echo "Temporary directory: $TMPDIR" 1>&2

#clean raw data
cat - | grep "\[[0-9\.]*\]" | sed 's_[^]]*\] __' | grep -v '"SYMBOLTHISISADOT"\|"ENDOFLINE"\|"SYMBOLINTERROGATIONMARK"\|"SYMBOLEXCLAMATIONMARK"' > $TMPDIR/oneperline

NUMLINE=0
while read line; do

	NUMLINE=`expr $NUMLINE + 1`
	echo "$line" | python $PYDIR/splitPartialParses.py > $TMPDIR/trees
	
	NUMTREE=0
	while read linetree; do
		NUMTREE=`expr $NUMTREE + 1`
		echo "vp -showfun $linetree | wf -file=$TMPDIR/tree.$NUMLINE.$NUMTREE.dot" >> $TMPDIR/gfinput
	done < $TMPDIR/trees
	

done < $TMPDIR/oneperline

cat $TMPDIR/gfinput | gf +RTS -K500M -RTS -run $PGF

#create svg files
for myfile in `find $TMPDIR -name 'tree.*.dot'`; do
	dot -Tsvg < $myfile > `echo "$myfile" | sed 's:\.dot$:.svg:'`
done

#join svg files
for number in `find $TMPDIR -name 'tree.*.svg' | sed -r 's:.*\.([0-9]+)\.[0-9]+.svg$:\1:' | sort | uniq`; do
	FILES=`find $TMPDIR -name "tree.$number.*.svg" | tr '\n' ' '`
	python $PYDIR/lib/svg_stack.py --direction=h --margin=0 $FILES > $DIR/tree.$number.svg
done

#remove tmp dir
if [ "${FLAGS_keep_tmp_dir}" == "${FLAGS_FALSE}" ]; then
	rm -Rf $TMPDIR
fi