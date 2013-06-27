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
    parser.add_argument('--only_print_scores',action='store_true')
    parser.add_argument('--bilingual_exprs',required=True)
    parser.add_argument('--use_synonyms')
    parser.add_argument('--inverse_synonyms',action='store_true')
    parser.add_argument('--invert_synonym_direction',action='store_true')
    parser.add_argument('--threshold',default='2')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    
    set_debug(args.debug)
    
    if args.use_synonyms:
        ParallelMWE.load_synonym_dict(args.use_synonyms, args.inverse_synonyms,args.invert_synonym_direction)
    
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
        if bilExpr.slexpr.get_non_leaf_funtions() == reprlistofnonleafs or args.only_print_scores:
            bilExprs.append(bilExpr)
    
    if args.only_print_scores:
        for mwe in mwes:
            mwe.compute_reproduced_and_matching_bilexprs([bilExpr for bilExpr in bilExprs if bilExpr.slexpr.get_non_leaf_funtions()== mwe.get_representative()])
            print mwe
    else:
        solution=select_mwes((mwes,bilExprs),int(args.threshold),0.0)
        for mwe in solution:
            print mwe

    #pool = Pool()
    #result = pool.map(abstractLearningLib.select_mwes , abstractLearningLib.MWEReader.s_groups)
    
