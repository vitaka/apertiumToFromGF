#!/usr/bin/env python

import sys
from lib.abstractLearningLib import split_partial_parse

if __name__ == "__main__":
    for line in sys.stdin:
        line=line.strip()
        for partial in split_partial_parse(line):
            print partial
