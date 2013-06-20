#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-

#relevant rules are those which:
# - SL side is different from TL side
# - At least explain $threshold examples
# - The right side is matched with the left side at least 51% of times the left side appears

import sys,argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='prints only fun name.')
    parser.add_argument('--threshold',default='2.0')
    args = parser.parse_args(sys.argv[1:])
    
    threshold=float(args.threshold)
    
    for line in sys.stdin:
        line=line.strip()
        parts=line.split(" | ")
        freq=int(parts[0].split(" ")[0])
        prop=float(parts[0].split(" ")[1])
        freqOfOption=freq*prop
        if freqOfOption >= threshold and parts[1] != parts[2] and prop > 0.5:
            print line
