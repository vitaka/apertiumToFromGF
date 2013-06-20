#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys,re, portApertiumToGFLib,argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Chooses alignment templates.')
    parser.add_argument('--open_categories',required=True)
    args = parser.parse_args(sys.argv[1:])
    
    opencategories=args.open_categories.split(",")
    
    for line in sys.stdin:
        line=line.decode('utf-8')
        parts = line.split("\t")
        slsentence=parts[0]
        tlsentence=parts[1]
        
        regex = re.compile("\^[^$]*\$")
        slwords=regex.findall(slsentence)
        
        tlwords=list()
        tlwordsraw=tlsentence.split("^*WORDMARKER$")
        for tlwordraw in tlwordsraw[:-1]:
            candidates=regex.findall(tlwordraw)
            if len(candidates) > 0:
                tlwords.append(candidates[0])
            else:
                tlwords.append("^*NOTRANSLATION$")
        
        
        print >> sys.stderr, "SL: "+str(slwords)
        print >> sys.stderr, "TL: "+str(tlwords)
        
        for i in range(len(slwords)):
            slw=portApertiumToGFLib.LexicalFormNoCategories()
            if not ( slwords[i][1:-1].startswith("*") or  slwords[i][1:-1].startswith("@")):
                slw.parse(slwords[i][1:-1])
            
            tlw=portApertiumToGFLib.LexicalFormNoCategories()
            if not ( tlwords[i][1:-1].startswith("*") or tlwords[i][1:-1].startswith("@") ):
                tlw.parse(tlwords[i][1:-1])
            
            if i>0:
                sys.stdout.write("\t")
            
            if len (slw.get_pos()) == 0:
                sys.stdout.write("*UNKNOWN")
            else:
                if slw.get_pos() in opencategories:
                    slw.remove_lemma()
                    sys.stdout.write((slw.to_apertium_format()+u"<TARGETLANGUAGE>"+tlw.get_tags_apertium_format()).encode('utf-8'))
                else:
                    sys.stdout.write(slw.to_apertium_format().encode('utf-8'))
        print ""
     