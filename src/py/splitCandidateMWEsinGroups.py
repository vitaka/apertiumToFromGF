'''
Created on 28/05/2013

@author: vitaka
'''

from lib.abstractLearningLib import MWEReader,ParallelMWE, MWESplitter
from lib.portApertiumToGFLib import MultipleLineEntriesProcessor
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chooses alignment templates.')
    parser.add_argument("--groups_dir",required=True)
    args = parser.parse_args(sys.argv[1:])
    
    groupSplitter=MWESplitter(args.groups_dir)
    MultipleLineEntriesProcessor.process(groupSplitter ,ParallelMWE)