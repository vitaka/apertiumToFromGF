#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-


import sys,pgf,argparse
from lib.abstractLearningLib import  ExtendedExpr 


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='prints only fun name.')
    parser.add_argument('--offset',default='0')
    args = parser.parse_args(sys.argv[1:])
    
    offset=int(args.offset)
    
    for line in sys.stdin:
        parts = line.split("|")
        slcontext=parts[0].strip()
        sl=parts[1].strip()
        tlcontext=parts[2].strip()
        tl=parts[3].strip()
        slrawexpr=pgf.readExpr(sl)
        tlrawexpr=pgf.readExpr(tl)
        slexpr=ExtendedExpr(slrawexpr,None)
        slexpr.compute_leaf_functions_recursively()
        tlexpr=ExtendedExpr(tlrawexpr,None)
        tlexpr.compute_leaf_functions_recursively()
        print  " | ".join([slcontext,slexpr.str_with_variables(),tlcontext, tlexpr.str_with_variables(slexpr.unsorted_open_leaf_functions)])