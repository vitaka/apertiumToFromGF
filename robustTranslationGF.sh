#! /bin/bash

CURDIR=`dirname $0`
SCRIPTSDIR="$CURDIR/src/scripts"
PYDIR="$CURDIR/src/py"

###############################################################
# Translates a natural text with the GF robust parser/translator
##############################################################

. $CURDIR/shflags
######################
# (compulsory)
# Source language of the GF grammar (e.g. ParseEng)
######################
DEFINE_string 'source_language' '' 'source language' 's'

######################
# (compulsory)
# target language of the GF grammar (e.g. ParseSpa)
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
# (optional,flag)
# Temporary directory where all the the files will be stored
# If not set, the script will create a new temporary directory under /tmp
######################
DEFINE_boolean 'keep_tmp_dir' 'false' 'do not remove temporal dir' 'k'

######################
# (optional,flag)
# Don't parse input. With this flag enabled, the input must be a set of trees already parsed.
######################
DEFINE_boolean 'input_is_tree_raw' 'false' 'The input is a set of trees' 'r'

######################
# (optional,flag)
# Don't translate. With this flag enabled, the output of the program is simply the result of parsing the input.
######################
DEFINE_boolean 'output_is_tree_raw' 'false' 'The output is a set of trees' 'w'

######################
# (optional,flag)
# Don't parse and don't translate. With this flag enabled, the output is simply the tokenization of the input
######################
DEFINE_boolean 'output_is_input_tokenized' 'false' 'Simply tokenize the input' 'n'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

TMPDIR=`mktemp -d`
echo "Temporary directory: $TMPDIR" 1>&2

FINISHED="no"

if [ "${FLAGS_input_is_tree_raw}" == "${FLAGS_FALSE}" ]; then

	#tokenize file. default language = English
	perl $SCRIPTSDIR/normalize-punctuation.perl en |  perl $SCRIPTSDIR/tokenizer.perl > $TMPDIR/input.tok

	# put ENDOFLINE marker at the end of each line of the input file |
	# segment each line in sentences |
	# remove initial space and empty lines |
	# lowercase first word of each sentence |
	# restore case of 'I' pronoun |
	# use symbol names for sentence delimiters
	cat $TMPDIR/input.tok | sed 's:$:\nENDOFLINE:'  |  sed 's_\(\.\|?\|!\)_\n\1\n_g' | sed 's_^ *__' | grep -v '^$' | sed 's_^\([ "]*\)\(.\)_\1\L\2_g' | sed 's_^\([ "]*\)i _\1I _g' | sed 's_^eNDOFLINE_ENDOFLINE_' | sed 's_^!$_SYMBOLEXCLAMATIONMARK_' | sed 's_^?$_SYMBOLINTERROGATIONMARK_' | sed 's_^\.$_SYMBOLTHISISADOT_' > $TMPDIR/input.tok.seg.oneperline

	if [ "${FLAGS_output_is_input_tokenized}" == "${FLAGS_TRUE}" ]; then
		cat  $TMPDIR/input.tok.seg.oneperline
		FINISHED="yes"
	else
		#call pgf-translate
		cat $TMPDIR/input.tok.seg.oneperline | pgf-translate ${FLAGS_source_pgf} Phr ${FLAGS_source_language} ${FLAGS_source_language} ParseEngAbs3.probs > $TMPDIR/trees.raw
	fi

else
	touch $TMPDIR/input.tok
	cat - >  $TMPDIR/trees.raw
fi

if [ "$FINISHED" != "yes" ]; then
	if [ "${FLAGS_output_is_tree_raw}" == "${FLAGS_TRUE}" ]; then

		cat $TMPDIR/trees.raw
		FINISHED="yes"
	else

		#build analysis debug information
		cat $TMPDIR/trees.raw | grep "\[[0-9\.]*\]" | sed 's_[^]]*\] __' | sed 's_.*"SYMBOLTHISISADOT".*_.//_' | sed 's_.*"SYMBOLEXCLAMATIONMARK".*_!//_' | sed 's_.*"SYMBOLINTERROGATIONMARK".*_?//_' | sed 's_.*"ENDOFLINE".*_|_' | tr -d '\n' | tr '|' '\n' > $TMPDIR/debug.trees

		#extract only relevant information: select only lines with [0.454756]. And split partial parses
		cat $TMPDIR/trees.raw  | grep "\[[0-9\.]*\]" | sed 's_[^]]*\] __' | python $PYDIR/splitPartialParses.py > $TMPDIR/trees.clean

		#linearize trees
		cat $TMPDIR/trees.clean | sed "s_^_l -lang=${FLAGS_target_language} _" | gf +RTS -K500M -RTS -run ${FLAGS_target_pgf} | grep -v "^$" | sed 's:Function \([^ ]*\) is not in scope:\1_not_in_scope:g' > $TMPDIR/output.tok.seg

		#build generation debug information
		cat $TMPDIR/output.tok.seg | tr  '\n' ' ' | sed 's_ENDOFLINE _\n_g' | sed 's_SYMBOLEXCLAMATIONMARK_//!_g' | sed 's_SYMBOLINTERROGATIONMARK_//?_g' | sed 's_SYMBOLTHISISADOT_//._g' > $TMPDIR/debug.output


		#join linearizations in the same line, detokenize and restore punctuation
		cat $TMPDIR/output.tok.seg | tr  '\n' ' ' | sed 's_ENDOFLINE _\n_g' | sed 's_SYMBOLEXCLAMATIONMARK_!_g' | sed 's_SYMBOLINTERROGATIONMARK_?_g' | sed 's_SYMBOLTHISISADOT_._g' | perl $SCRIPTSDIR/detokenizer.perl | perl $SCRIPTSDIR/normalize-punctuation.perl es

		#print debug information
		paste -d '|' $TMPDIR/input.tok $TMPDIR/debug.trees $TMPDIR/debug.output 1>&2

	fi
fi

#remove tmp dir
if [ "${FLAGS_keep_tmp_dir}" == "${FLAGS_FALSE}" ]; then
	rm -Rf $TMPDIR
fi
