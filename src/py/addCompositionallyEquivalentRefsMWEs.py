'''
Created on 24/05/2013

@author: vitaka
'''
#!/usr/local/bin/python
# encoding: utf-8

from lib.abstractLearningLib import ParallelMWE, set_debug, \
    GFProbabilisticBilingualDictionary, ParallelMWESet
import argparse
import gzip
import sys

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Chooses rules.')
    parser.add_argument('--use_synonyms')
    parser.add_argument('--additional_references')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    set_debug(args.debug)
    
    #read synonyms
    if args.use_synonyms:
        probBilDic=GFProbabilisticBilingualDictionary()
        myfile=open(args.use_synonyms,'r')
        probBilDic.read(myfile)
        myfile.close()
        ParallelMWE.synonymDict=probBilDic.generate_synonim_dict()
    
    mweset=ParallelMWESet()
    
    if args.additional_references:
        myfile=gzip.open(args.additional_references)
        for line in myfile:
            mwe=ParallelMWE()
            mwe.parse(line)
            mweset.add(mwe)
        myfile.close()
    
    #read mwes
    mwelist=list()
    for line in sys.stdin:
        line=line.strip()
        mwe=ParallelMWE()
        mwe.parse(line)
        mweset.add(mwe)
        mwelist.append(mwe)
    
    for mwe in mwelist:
        mwe.add_refs_to_sub(mweset)
        print mwe
    
    
        
        
