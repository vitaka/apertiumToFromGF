# ! /bin/bash
CURDIR=`dirname $0`

############################################
# 
#
############################################<<<


#shflags
. ./shflags
DEFINE_string 'sl_mono_dictionary' '' 'SL monolingual dictionary' 'd'
DEFINE_string 'tl_mono_dictionary' '' 'TL monolingual dictionary' 't'
DEFINE_string 'bi_dictionary' '' 'bilingual dictionary' 'b'
DEFINE_string 'black_list' '' 'File containint list of tokens which are already present in GF' 'l'
DEFINE_boolean 'only_abstract' 'false' 'print only abstract syntax tokens' 'a'
DEFINE_string 'valencies_from_dict' '' 'GF dictionary file from which valencies are extracted' 'v'
DEFINE_boolean 'no_multiwords' 'false' 'do not generate multiword entries' 'n'
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"

CURDIR=`dirname $0`
PYDIR=$CURDIR/src/py


if [ "${FLAGS_only_abstract}" == "${FLAGS_TRUE}" ] ; then
PRINT_ONLY_TOKENS_FLAG="--print_only_tokens"
else
PRINT_ONLY_TOKENS_FLAG=""
fi

if [ "${FLAGS_no_multiwords}" == "${FLAGS_TRUE}" ] ; then
NO_MULTIWORDS_FLAG="--no_multiwords"
else
NO_MULTIWORDS_FLAG=""
fi

if [ "${FLAGS_black_list}" != "" ] ; then
BLACK_LIST_FLAG="--black_list ${FLAGS_black_list}"
else
BLACK_LIST_FLAG=""
fi

FILTERED_VALENCIES_FILE=`mktemp`
USE_VALENCIES_FLAG=""
if [ "${FLAGS_valencies_from_dict}" != "" ]; then
	cat ${FLAGS_valencies_from_dict} | grep "_V" | LC_ALL=C sort > $FILTERED_VALENCIES_FILE
	USE_VALENCIES_FLAG="--valencies $FILTERED_VALENCIES_FILE"
fi

if [ "${FLAGS_sl_mono_dictionary}" != "" ]; then

if [ ${FLAGS_only_abstract} -eq ${FLAGS_TRUE} ] ; then
	echo 'abstract ApertiumLexicon = Cat ** {'
	echo 'fun'
else
	echo '--# -path=.:prelude'
	echo 'concrete ApertiumLexiconEng of ApertiumLexicon = CatEng **'
	echo '  open ParadigmsEng, IrregEng, Prelude in {'
	echo 'flags '
	echo '  optimize=values ;'
fi


#ENGLISH ADJECTIVES
lt-expand ${FLAGS_sl_mono_dictionary} | grep -v -F ":<:" | grep -F "<adj>" | sed 's_:>:_:_' | awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq | python $PYDIR/generateGFWords.py --lang en --category adj $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

#ENGLISH NOUNS
lt-expand ${FLAGS_sl_mono_dictionary} |  grep -v -F ":<:" | grep -v -F "__REGEXP__" | grep -F "<n>" | sed 's_:>:_:_' | awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq | sed "s:\\+'s<gen>:<genitivesaxon>:g" | sed 's_^_^_' | sed 's_:_$[:_' | sed 's_$_]_' | apertium-pretransfer | sed 's_^^__' | sed 's_\$\[__' | sed 's_]$__' | LC_ALL=C sort | python $PYDIR/generateGFWords.py --category n --lang en $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

#ENGLISH PROPER NOUNS
lt-expand ${FLAGS_sl_mono_dictionary} | grep -F "<np>" | grep -v -F ":<:" | sed 's_:>:_:_' | awk -F":" '{print $2 ":"  $1 ;}' |grep -v -F  "+'s<gen>"  |  LC_ALL=C sort | uniq | python $PYDIR/generateGFWords.py --category np --lang en $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

#ENGLISH VERBS
lt-expand ${FLAGS_sl_mono_dictionary} | grep -v -F ":<:" | grep -F "<vblex>" | sed 's_:>:_:_' | awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq   |  sed "s:\\+prpers[^#]*#:<hasprpers>#:" | sed "s:\\+this[^#]*#:<hasthis>#:" |  sed "s:\\+that[^#]*#:<hasthat>#:"  |  sed 's_^_^_' | sed 's_:_$[:_' | sed 's_$_]_' | apertium-pretransfer | sed 's_^^__' | sed 's_\$\[__' | sed 's_]$__' | grep -v -F "^" | LC_ALL=C sort | python $PYDIR/generateGFWords.py --category vblex --lang en $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $USE_VALENCIES_FLAG $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

#ENGLISH ADVERBS
lt-expand ${FLAGS_sl_mono_dictionary} | grep -v -F ":<:" | grep -F "<adv>" | grep -v -F "<vblex>" | grep -v -F "<vaux>"  | sed 's_:>:_:_' | awk -F":" '{print $2 ":"  $1 ;}' |  LC_ALL=C sort | uniq | python $PYDIR/generateGFWords.py --category adv --lang en $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

if [ ${FLAGS_only_abstract} -eq ${FLAGS_TRUE} ] ; then
	echo '}'
else
	echo '};'
fi

fi


if [ "${FLAGS_tl_mono_dictionary}" != "" ]; then

echo '--# -path=.:../romance:../common:../abstract:../../prelude'
echo 'concrete ApertiumLexiconSpa of ApertiumLexicon = CatSpa ** open MorphoSpa, BeschSpa,  ParadigmsSpa, Prelude  in {'
echo 'flags '
echo '  optimize=values ;'

if [ "${FLAGS_bi_dictionary}" == "" ]; then
	echo "Bilingual dictionary is required to generate TL adjectives"
	flags_help
	exit
fi

#SPANISH ADJECTIVES

EXPANDED_DICTIONARY_FILE=`mktemp`

#expand bilingual dictionary for adjectives
lt-expand ${FLAGS_bi_dictionary}  | grep -F "<adj>" | grep -v -F ":<:" | sed 's_:>:_:_' |  awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq > $EXPANDED_DICTIONARY_FILE

#extract Spanish adjectives
lt-expand  ${FLAGS_tl_mono_dictionary} | grep -v -F ":>:" | grep -F "<adj>" | sed 's_:<:_:_' | awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq | sed 's_^_^_' | sed 's_:_$[:_' | sed 's_$_]_' | apertium-pretransfer | sed 's_^^__' | sed 's_\$\[__' | sed 's_]$__' | LC_ALL=C sort |  python $PYDIR/generateGFWords.py --category adj --lang es --bildic_tl_expanded_file $EXPANDED_DICTIONARY_FILE $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

#SPANISH NOUNS
#expand bilingual dictionary for nouns
lt-expand ${FLAGS_bi_dictionary}  | grep -F "<n>" | grep -v -F ":<:" | sed 's_:>:_:_' |  awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq > $EXPANDED_DICTIONARY_FILE 

#extract Spanish nouns
lt-expand  ${FLAGS_tl_mono_dictionary} | grep -v -F ":>:" | grep -F "<n>" | sed 's_:<:_:_' | awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq | sed 's_^_^_' | sed 's_:_$[:_' | sed 's_$_]_' | apertium-pretransfer | sed 's_^^__' | sed 's_\$\[__' | sed 's_]$__' | LC_ALL=C sort | python $PYDIR/generateGFWords.py --category n --lang es --bildic_tl_expanded_file $EXPANDED_DICTIONARY_FILE $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

#SPANISH PROPER NOUNS
#expand bilingual dictionary
lt-expand ${FLAGS_bi_dictionary}  | grep -F "<np>" | grep -v -F ":<:" | sed 's_:>:_:_' |  awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq > $EXPANDED_DICTIONARY_FILE

#extract Spanish proper nouns
lt-expand  ${FLAGS_tl_mono_dictionary} | grep -F "<np>" | grep -v -F ":>:" | sed 's_:<:_:_' | awk -F":" '{print $2 ":"  $1 ;}' | python $PYDIR/generateGFWords.py --category np --lang es --bildic_tl_expanded_file $EXPANDED_DICTIONARY_FILE $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

#SPANISH VERBS
#expand birbslingual dictionary for verbs
lt-expand ${FLAGS_bi_dictionary}  | grep -F "<vblex>" | grep -v -F ":<:" | sed 's_:>:_:_' |  awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq > $EXPANDED_DICTIONARY_FILE 

#extract Spanish verbs
lt-expand  ${FLAGS_tl_mono_dictionary} | grep -v -F ":>:" | grep -F "<vblex>" | sed 's_:<:_:_' | awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq   | grep -v -F "prpers" | grep -v -F "se<prn>" | grep -v -F "lo<prn>" |  sed 's_^_^_' | sed 's_:_$[:_' | sed 's_$_]_' | apertium-pretransfer | sed 's_^^__' | sed 's_\$\[__' | sed 's_]$__' | LC_ALL=C sort | python $PYDIR/generateGFWords.py --category vblex --lang es  $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $USE_VALENCIES_FLAG --bildic_tl_expanded_file $EXPANDED_DICTIONARY_FILE $NO_MULTIWORDS_FLAG | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

#SPANISH ADVERBS
#expand bilingual dictionary for adverbs
lt-expand ${FLAGS_bi_dictionary}  | grep -F "<adv>" | grep -v -F ":<:" | sed 's_:>:_:_' |  awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq > $EXPANDED_DICTIONARY_FILE

#extract Spanish adverbs
lt-expand  ${FLAGS_tl_mono_dictionary} | grep -v -F ":>:" | grep -F "<adv>"  | sed 's_:<:_:_' | awk -F":" '{print $2 ":"  $1 ;}' | LC_ALL=C sort | uniq   | sed 's_+,<cm>:\([^,]*\),_:\1_' | python $PYDIR/generateGFWords.py --category adv --lang es --bildic_tl_expanded_file $EXPANDED_DICTIONARY_FILE $PRINT_ONLY_TOKENS_FLAG $BLACK_LIST_FLAG $NO_MULTIWORDS_FLAG  | iconv --to-code='ISO-8859-1//TRANSLIT' --from-code=UTF-8

rm $EXPANDED_DICTIONARY_FILE 

echo 'oper'
echo '   mk4A a b c d = '
echo '   compADeg { s = \\_ => table {'
echo '       AF Masc n => numForms a c ! n ;'
echo '       AF Fem  n => numForms b d ! n ;'
echo '       AA        => ( mkAdjReg a ).s ! AA '
echo '       } ; isPre = False ; lock_A = <> } ;'
echo '  mk4A : (solo,sola,solos,solas : Str) -> A ;'
echo ''
echo 'oper allforms_67 : Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Str -> Verbum = \form1, form2, form3, form4, form5, form6, form7, form8, form9, form10, form11, form12, form13, form14, form15, form16, form17, form18, form19, form20, form21, form22, form23, form24, form25, form26, form27, form28, form29, form30, form31, form32, form33, form34, form35, form36, form37, form38, form39, form40, form41, form42, form43, form44, form45, form46, form47, form48, form49, form50, form51, form52, form53, form54, form55, form56, form57, form58, form59, form60, form61, form62, form63, form64, form65, form66, form67 ->'
echo '{s = table {'
echo '    VI Infn => form1 ;'
echo '    VI Ger => form2 ;'
echo '    VI Part => form3 ;'
echo '    VPB (Pres Ind Sg P1) => form4 ;'
echo '    VPB (Pres Ind Sg P2) => form5 ;'
echo '    VPB (Pres Ind Sg P3) => form6 ;'
echo '    VPB (Pres Ind Pl P1) => form7 ;'
echo '    VPB (Pres Ind Pl P2) => form8 ;'
echo '    VPB (Pres Ind Pl P3) => form9 ;'
echo '    VPB (Pres Sub Sg P1) => form10 ;'
echo '    VPB (Pres Sub Sg P2) => form11 ;'
echo '    VPB (Pres Sub Sg P3) => form12 ;'
echo '    VPB (Pres Sub Pl P1) => form13 ;'
echo '    VPB (Pres Sub Pl P2) => form14 ;'
echo '    VPB (Pres Sub Pl P3) => form15 ;'
echo '    VPB (Impf Ind Sg P1) => form16 ; --# notpresent'
echo '    VPB (Impf Ind Sg P2) => form17 ; --# notpresent'
echo '    VPB (Impf Ind Sg P3) => form18 ; --# notpresent'
echo '    VPB (Impf Ind Pl P1) => form19 ; --# notpresent'
echo '    VPB (Impf Ind Pl P2) => form20 ; --# notpresent'
echo '    VPB (Impf Ind Pl P3) => form21 ; --# notpresent'
echo '    VPB (Impf Sub Sg P1) => form22 ; --# notpresent'
echo '    VPB (Impf Sub Sg P2) => form23 ; --# notpresent'
echo '    VPB (Impf Sub Sg P3) => form24 ; --# notpresent'
echo '    VPB (Impf Sub Pl P1) => form25 ; --# notpresent'
echo '    VPB (Impf Sub Pl P2) => form26 ; --# notpresent'
echo '    VPB (Impf Sub Pl P3) => form27 ; --# notpresent'
echo '    VPB (ImpfSub2 Sg P1) => form28 ; --# notpresent'
echo '    VPB (ImpfSub2 Sg P2) => form29 ; --# notpresent'
echo '    VPB (ImpfSub2 Sg P3) => form30 ; --# notpresent'
echo '    VPB (ImpfSub2 Pl P1) => form31 ; --# notpresent'
echo '    VPB (ImpfSub2 Pl P2) => form32 ; --# notpresent'
echo '    VPB (ImpfSub2 Pl P3) => form33 ; --# notpresent'
echo '    VPB (Pret Sg P1) => form34 ; --# notpresent'
echo '    VPB (Pret Sg P2) => form35 ; --# notpresent'
echo '    VPB (Pret Sg P3) => form36 ; --# notpresent'
echo '    VPB (Pret Pl P1) => form37 ; --# notpresent'
echo '    VPB (Pret Pl P2) => form38 ; --# notpresent'
echo '    VPB (Pret Pl P3) => form39 ; --# notpresent'
echo '    VPB (Fut Ind Sg P1) => form40 ; --# notpresent'
echo '    VPB (Fut Ind Sg P2) => form41 ; --# notpresent'
echo '    VPB (Fut Ind Sg P3) => form42 ; --# notpresent'
echo '    VPB (Fut Ind Pl P1) => form43 ; --# notpresent'
echo '    VPB (Fut Ind Pl P2) => form44 ; --# notpresent'
echo '    VPB (Fut Ind Pl P3) => form45 ; --# notpresent'
echo '    VPB (Fut Sub Sg P1) => form46 ; --# notpresent'
echo '    VPB (Fut Sub Sg P2) => form47 ; --# notpresent'
echo '    VPB (Fut Sub Sg P3) => form48 ; --# notpresent'
echo '    VPB (Fut Sub Pl P1) => form49 ; --# notpresent'
echo '    VPB (Fut Sub Pl P2) => form50 ; --# notpresent'
echo '    VPB (Fut Sub Pl P3) => form51 ; --# notpresent'
echo '    VPB (Cond Sg P1) => form52 ; --# notpresent'
echo '    VPB (Cond Sg P2) => form53 ; --# notpresent'
echo '    VPB (Cond Sg P3) => form54 ; --# notpresent'
echo '    VPB (Cond Pl P1) => form55 ; --# notpresent'
echo '    VPB (Cond Pl P2) => form56 ; --# notpresent'
echo '    VPB (Cond Pl P3) => form57 ; --# notpresent'
echo '    VPB (Imper Sg P1) => form58 ;'
echo '    VPB (Imper Sg P2) => form59 ;'
echo '    VPB (Imper Sg P3) => form60 ;'
echo '    VPB (Imper Pl P1) => form61 ;'
echo '    VPB (Imper Pl P2) => form62 ;'
echo '    VPB (Imper Pl P3) => form63 ;'
echo '    VPB (Pass Sg Masc) => form64 ;'
echo '    VPB (Pass Sg Fem) => form65 ;'
echo '    VPB (Pass Pl Masc) => form66 ;'
echo '    VPB (Pass Pl Fem) => form67'
echo '    } } ;'
echo '};'

fi

rm $FILTERED_VALENCIES_FILE
