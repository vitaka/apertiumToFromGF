# ! /bin/bash
CURDIR=`dirname $0`

#Analyses the SL side of the test corpus and adds the TL tags the words of open categories

#SL CORPUS=stdin

#shflags
. $CURDIR/shflags
DEFINE_string 'open_categories' '' 'Open lexical categories, separated by comma (,) ' 'o'
DEFINE_string 'original_mode' '' 'Original mode file' 'm'
DEFINE_boolean 'keep_tmp_dir' 'false' 'do not remove temporal dir' 'k'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"


TMPDIR=`mktemp -d`

echo "TMPDIR: $TMPDIR" 1>&2

#create analysis mode
mkdir -p $TMPDIR/modes
cat ${FLAGS_original_mode} | awk -F"apertium-pretransfer" '{print $1}' | sed 's:| *$:| apertium-pretransfer:' > $TMPDIR/modes/analyse.mode

#analyse text
 cat - | apertium -d $TMPDIR analyse | apertium-pretransfer | sed 's:\$<:\\$<:g' > $TMPDIR/text.analysed
 
#translate word-for-word
#(but first compile empty rules)
cp $CURDIR/empty-rules-for-translating.t1x $TMPDIR/
apertium-preprocess-transfer $TMPDIR/empty-rules-for-translating.t1x $TMPDIR/empty-rules-for-translating.bin
#(and find bilingual dictionary)
BILINGUAL_DICT=`cat ${FLAGS_original_mode} | grep -E -o 'apertium-transfer +[^-][^|]*\|' | grep -E -o ' [^ ]*autobil[^ ]*'`

cat $TMPDIR/text.analysed |  sed 's_\([^\]\)\$_\1$^*WORDMARKER$_g' | apertium-transfer $TMPDIR/empty-rules-for-translating.t1x $TMPDIR/empty-rules-for-translating.bin $BILINGUAL_DICT > $TMPDIR/text.translated

paste $TMPDIR/text.analysed $TMPDIR/text.translated | sed 's:\\\$:DOLLARSYMBOL:g' | python $CURDIR/addTLTags.py --open_categories ${FLAGS_open_categories} 

#remove tmp dir
if [ "${FLAGS_keep_tmp_dir}" == "${FLAGS_FALSE}" ]; then
	rm -Rf $TMPDIR
fi
