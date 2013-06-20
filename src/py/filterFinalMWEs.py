#!/usr/local/bin/python
# encoding: utf-8

import sys,argparse
from lib.abstractLearningLib import ParallelMWE

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='filter final MWEs')
    parser.add_argument('--different_sides',action='store_true')
    parser.add_argument('--contains_lexical',action='store_true')
    parser.add_argument('--not_contains_lexical',action='store_true')
    parser.add_argument('--contains_non_wildcard',action='store_true')
    parser.add_argument('--contains_wildcard',action='store_true')
    parser.add_argument('--not_contains_wildcard',action='store_true')
    args = parser.parse_args(sys.argv[1:])
    
    inputSource=sys.stdin
    
    for line in inputSource:
        line=line.strip()
        mwe=ParallelMWE()
        mwe.parse(line)
        
        isValid=True
        
        if args.different_sides:
            isValid = isValid and not mwe.is_equal_sides()
        
        if args.contains_lexical:
            isValid = isValid and ( len(mwe.slexpr.get_open_leaf_functions())>0 or len(mwe.tlexpr.get_open_leaf_functions())>0 )
        
        if args.not_contains_lexical:
            isValid = isValid and not ( len(mwe.slexpr.get_open_leaf_functions())>0 or len(mwe.tlexpr.get_open_leaf_functions())>0 )
        
        if args.contains_non_wildcard:
            isValid = isValid and ( len(mwe.slexpr.get_non_wildcard_leaf_functions())>0 and len(mwe.tlexpr.get_non_wildcard_leaf_functions())>0 )
        
        if args.contains_wildcard:
            isValid = isValid and mwe.get_total_wildcards() > 0
        
        if args.not_contains_wildcard:
            isValid = isValid and mwe.get_total_wildcards() == 0
            
        if isValid:
            print line  
