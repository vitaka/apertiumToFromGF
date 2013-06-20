#! /bin/bash

# processes the raw output of pgf-translate (stdin) and 
# creates a tree representation in .eps format for each line
# of the output. 

CURDIR=`dirname $0`
PYDIR=$CURDIR/src/py

#shflags
. $CURDIR/shflags
DEFINE_string 'dir_1' '' 'directory where the trees of the first language are stored' 's'
DEFINE_string 'dir_2' '' 'directory where the trees of the second language are stored' 't'
DEFINE_string 'dir_output' '' 'directory where the joint trees will be stored' 'o'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

DIR1=${FLAGS_dir_1}
DIR2=${FLAGS_dir_2}
DIROUTPUT=${FLAGS_dir_output}

mkdir -p $DIROUTPUT
for file in `ls $DIR1/`; do 
	python $PYDIR/svg_stack.py --direction=h --margin=100 $DIR1/$file $DIR2/$file >$DIROUTPUT/$file  ;   
done