#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys,pgf,argparse
from lib.abstractLearningLib import ExtendedExpr



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='prints only fun name.')
    parser.add_argument('--offset',default='0')
    args = parser.parse_args(sys.argv[1:])
    
    offset=int(args.offset)
    
    for line in sys.stdin:
        
        parts = line.split("|")
        sl=parts[0+offset].strip()
        tl=parts[1+offset].strip()
        slrawexpr=pgf.readExpr(sl)
        tlrawexpr=pgf.readExpr(tl)
        slexpr=ExtendedExpr(slrawexpr,None)
        tlexpr=ExtendedExpr(tlrawexpr,None)
        print " | ".join( [ parts[i].strip() for i in range(offset)] + [slexpr.str_with_children_fun(),tlexpr.str_with_children_fun()])