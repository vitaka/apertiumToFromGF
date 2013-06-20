#! /bin/bash

#Takes original DictEng.gf or DictEngAbs.gf, removes words from open categories, restores entries originally from GF used in the Spanish side, i.e., words in LexiconSpa

DICTENGFILE=$1
WHITELIST=$2

OPENCATEGORIES="A A2 AdA AdN AdV Adv N N2 PN V V2 V2A V2Q V2S V2V V3 VA VQ VS VV"
GREPEXPR=""
for c in $OPENCATEGORIES; do
	GREPEXPR="$GREPEXPR\|_$c "
done
GREPEXPRF=`echo "$GREPEXPR" | sed 's/^..//'`

TMPDIR=`mktemp -d`

cat $DICTENGFILE | tr '\n' ' ' | sed 's_ lin _\nlin _g' | sed 's_fun _\nfun _g'  | sed 's_} *$_\n}\n_' > $TMPDIR/dictprocessed

cat $TMPDIR/dictprocessed | grep -v "$GREPEXPRF" | grep -v "^    " > $TMPDIR/dictWithoutOpen

for WORD in `cat $WHITELIST`; do
	cat $TMPDIR/dictprocessed | grep " $WORD " >> $TMPDIR/dictOpenRestored
done

#put newline after --# notpresent
cat $TMPDIR/dictWithoutOpen $TMPDIR/dictOpenRestored | grep -v "^ *} *$" | sed '$s/$/}/' | sed 's:\(--# [^ ]*\):\1\n:g'

rm -Rf $TMPDIR