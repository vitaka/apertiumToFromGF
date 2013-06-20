#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-

from lib.abstractLearningLib import BilingualExpr, ParallelMWE, \
    select_mwes, set_debug, GFProbabilisticBilingualDictionary
import argparse
import gzip
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='select minimum amount of parallel MWEs to reproduce the bilingual expr.')
    parser.add_argument('--bilingual_exprs',required=True)
    parser.add_argument('--use_synonyms')
    parser.add_argument('--threshold',default='2')
    parser.add_argument('--min_prop_reproduced',default='0.66')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    
    set_debug(args.debug)
    
    if args.use_synonyms:
        probBilDic=GFProbabilisticBilingualDictionary()
        myfile=open(args.use_synonyms,'r')
        probBilDic.read(myfile)
        myfile.close()
        ParallelMWE.synonymDict=probBilDic.generate_synonim_dict()
    
    mwes=list()
    #read MWEs
    for line in sys.stdin:
        line=line.strip()
        mwe=ParallelMWE()
        mwe.parse(line)
        mwes.append(mwe)
    
    reprlistofnonleafs=mwes[0].get_representative()
    
    bilExprs=list()
    #read bilingual exprs
    for line in gzip.open(args.bilingual_exprs,'r'):
        line=line.strip()
        bilExpr=BilingualExpr()
        bilExpr.parse(line)
        if bilExpr.slexpr.get_non_leaf_funtions() == reprlistofnonleafs:
            bilExprs.append(bilExpr)
    
    solution=select_mwes((mwes,bilExprs),int(args.threshold),0.0)
    for mwe in solution:
        print mwe

    #pool = Pool()
    #result = pool.map(abstractLearningLib.select_mwes , abstractLearningLib.MWEReader.s_groups)
    
