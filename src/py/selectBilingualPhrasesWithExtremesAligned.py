#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys

if __name__ == "__main__":
    for line in sys.stdin:
        parts=line.split(" ||| ")
        numSLWords=len(parts[0].split(" "))
        numTLWords=len(parts[1].split(" "))
        alignments=[ (int(alstr.split("-")[0]) ,int(alstr.split("-")[1])) for alstr in parts[2].split(" ")]
        sl0als=[al for al in alignments if al[0]==0]
        tl0als=[al for al in alignments if al[1]==0]
        slendals=[al for al in alignments if al[0]==numSLWords-1]
        tlendals=[al for al in alignments if al[1]==numTLWords-1]
        
        if len(sl0als) > 0 and len(tl0als) > 0 and len(slendals) > 0 and len(tlendals) > 0:
            print line.strip()
    