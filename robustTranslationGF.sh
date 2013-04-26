#! /bin/bash

CURDIR=`dirname $0`

#shflags
. $CURDIR/shflags
DEFINE_string 'source_language' '' 'source language' 's'
DEFINE_string 'target_language' '' 'target language' 't'
DEFINE_string 'source_pgf' '' 'source language PGF' 'o'
DEFINE_string 'target_pgf' '' 'target language PGF' 'a'
DEFINE_boolean 'keep_tmp_dir' 'false' 'do not remove temporal dir' 'k'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

TMPDIR=`mktemp -d`
echo "Temporary directory: $TMPDIR" 1>&2

#tokenize file. default language = English
perl $CURDIR/tokenizer.perl > $TMPDIR/input.tok

#segment file | lowercase first word | uppercase again if it is I | remove empty groups at the end | add end of sentence marker | put one segment per line | remove starting and ending whitespaces
#cat $TMPDIR/input.tok | tr '.?!' '|' | sed 's_\(^\|| \)\(.\)_\1\L\2_g' | sed 's_\(^\|| \)i_\1I _g' | sed 's_ | *$__' | sed 's:$: | ENDOFLINE:' | tr '|' '\n' | sed 's_^ *__' | sed 's_ *$__' > $TMPDIR/input.tok.seg.oneperline

# put ENDOFLINE marker at the end of each line of the input file |
# segment each line in sentences |
# remove initial space and empty lines |
# lowercase first word of each sentence |
# restore case of 'I' pronoun |
# use symbol names for sentence delimiters
cat $TMPDIR/input.tok | sed 's:$:\nENDOFLINE:'  |  sed 's_\(\.\|?\|!\)_\n\1\n_g' | sed 's_^ *__' | grep -v '^$' | sed 's_^\([ "]*\)\(.\)_\1\L\2_g' | sed 's_^\([ "]*\)i _\1I _g' | sed 's_^eNDOFLINE_ENDOFLINE_' | sed 's_^!$_SYMBOLEXCLAMATIONMARK_' | sed 's_^?$_SYMBOLINTERROGATIONMARK_' | sed 's_^\.$_SYMBOLTHISISADOT_' > $TMPDIR/input.tok.seg.oneperline

#call pgf-translate
cat $TMPDIR/input.tok.seg.oneperline | pgf-translate ${FLAGS_source_pgf} Phr ${FLAGS_source_language} ${FLAGS_source_language} ParseEngAbs3.probs > $TMPDIR/trees.raw

#build analysis debug information
cat $TMPDIR/trees.raw | grep "\[[0-9\.]*\]" | sed 's_[^]]*\] __' | sed 's_.*"SYMBOLTHISISADOT".*_.//_' | sed 's_.*"SYMBOLEXCLAMATIONMARK".*_!//_' | sed 's_.*"SYMBOLINTERROGATIONMARK".*_?//_' | sed 's_.*"ENDOFLINE".*_|_' | tr -d '\n' | tr '|' '\n' > $TMPDIR/debug.trees

#extract only relevant information: select only lines with [0.454756]. And split partial parses
cat $TMPDIR/trees.raw  | grep "\[[0-9\.]*\]" | sed 's_[^]]*\] __' | python $CURDIR/splitPartialParses.py > $TMPDIR/trees.clean

#linearize trees
cat $TMPDIR/trees.clean | sed "s_^_l -lang=${FLAGS_target_language} _" | gf +RTS -K500M -RTS -run ${FLAGS_target_pgf} | grep -v "^$" | sed 's:Function \([^ ]*\) is not in scope:\1_not_in_scope:g' > $TMPDIR/output.tok.seg

#build generation debug information
cat $TMPDIR/output.tok.seg | tr  '\n' ' ' | sed 's_ENDOFLINE _\n_g' | sed 's_SYMBOLEXCLAMATIONMARK_//!_g' | sed 's_SYMBOLINTERROGATIONMARK_//?_g' | sed 's_SYMBOLTHISISADOT_//._g' > $TMPDIR/debug.output


#join linearizations in the same line, detokenize and restore punctuation
cat $TMPDIR/output.tok.seg | tr  '\n' ' ' | sed 's_ENDOFLINE _\n_g' | sed 's_SYMBOLEXCLAMATIONMARK_!_g' | sed 's_SYMBOLINTERROGATIONMARK_?_g' | sed 's_SYMBOLTHISISADOT_._g' | perl $CURDIR/detokenizer.perl | perl $CURDIR/normalize-punctuation.perl es

#print debug information
paste -d '|' $TMPDIR/input.tok $TMPDIR/debug.trees $TMPDIR/debug.output 1>&2

#remove tmp dir
if [ "${FLAGS_keep_tmp_dir}" == "${FLAGS_FALSE}" ]; then
	rm -Rf $TMPDIR
fi
