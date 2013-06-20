#! /bin/bash

# Computes some statistics about the parsing performance 
# Takes as an input the directory created by learnAbstractSyntax.sh
#

CURDIR=`dirname $0`
PYDIR=$CURDIR/src/py

#shflags
. $CURDIR/shflags
DEFINE_string 'dir' './mwes-h10000' 'directory where the parsed sentence are stored' 'd'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

DIR=${FLAGS_dir}

NUMSENTENCESFULLYPARSED_SL=`cat $DIR/trees.clean.sl | grep "^[^?]" | wc -l`

NUMSENTENCESFULLYPARSED_TL=`cat $DIR/trees.clean.tl | grep "^[^?]" | wc -l`

NUMSENTENCESFULLYPARSED_BOTH=`paste -d '|' $DIR/trees.clean.sl $DIR/trees.clean.tl | sed 's:^[?].*:BUUU:' | sed 's:|?.*:BUUU:' | grep -v "BUUU" | wc -l`

echo "Sentences fully parsed SL: $NUMSENTENCESFULLYPARSED_SL"
echo "Sentences fully parsed TL: $NUMSENTENCESFULLYPARSED_TL"
echo "Sentences fully parsed itersection: $NUMSENTENCESFULLYPARSED_BOTH"

echo "Summary: $NUMSENTENCESFULLYPARSED_SL $NUMSENTENCESFULLYPARSED_TL $NUMSENTENCESFULLYPARSED_BOTH"