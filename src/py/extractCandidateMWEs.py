#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-

from lib.abstractLearningLib import BilingualExpr, set_debug, \
    GFProbabilisticBilingualDictionary, ParallelMWE
import sys
import argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Chooses rules.')
    parser.add_argument('--use_synonyms')
    parser.add_argument('--inverse_synonyms',action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    
    set_debug(args.debug)
    
    if args.use_synonyms:
        ParallelMWE.load_synonym_dict(args.use_synonyms, args.inverse_synonyms)
    
    for line in sys.stdin:
    #for line in ['1 | BaseNP (UsePN (SymbPN (MkSymb "Wilders"))) (DetCN (DetQuant (PossPron he_Pron) NumPl) (UseN supporter_N)) | BaseNP (UsePN (SymbPN (MkSymb "Wilders"))) (DetCN (DetQuant (PossPron it_Pron) NumPl) (UseN backer_N))']:
        line=line.strip()
        bilExpr=BilingualExpr()
        bilExpr.parse(line)
        for candidatemwe in bilExpr.extract_candidate_mwes():
            print candidatemwe
