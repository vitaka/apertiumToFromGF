#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-

from lib.portApertiumToGFLib import AbstractLineEntry,AbstractGroupProcessor,MultipleLineEntriesProcessor

class TreeTransformationEntry(AbstractLineEntry):
    def __init__(self):
        self.freq=0
        self.sltree=None
        self.tltree=None
    
    def parse(self,rawstr):
        parts=rawstr.split("|")
        self.freq=int(parts[0])
        self.sltree=parts[1].strip()
        self.tltree=parts[2].strip()
    
    def get_representative(self):
        return self.sltree

class TreeTransformationGrouper(AbstractGroupProcessor):
    @staticmethod
    def process(mygroup):
        totalfreq=0
        for entry in mygroup:
            totalfreq+=entry.freq
        
        #print SL side
        print str(totalfreq)+" | "+mygroup[0].sltree
        
        #print different TL sides
        for entry in mygroup:
            print "\t"+str(entry.freq)+" "+str(entry.freq*1.0/totalfreq)+" | "+entry.tltree


if __name__ == "__main__":
    MultipleLineEntriesProcessor.process(TreeTransformationGrouper,TreeTransformationEntry)
