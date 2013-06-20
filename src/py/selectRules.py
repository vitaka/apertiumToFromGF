#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-


import sys, pgf, argparse
from lib.abstractLearningLib import PairTabReader,Model1Processor,DEBUG

DEBUG=False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chooses rules.')
    parser.add_argument('--model')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    DEBUG=args.debug
    DEBUG=args.debug
    
    PairTabReader.process(Model1Processor)
    print >> sys.stderr, "Processing finished. Model explains: "+str(Model1Processor.numExamplesReproduced)+ "/" + str(Model1Processor.numExamplesProcessed) +"("+ str(Model1Processor.numExamplesReproduced*1.0/Model1Processor.numExamplesProcessed) +"% ) of examples"