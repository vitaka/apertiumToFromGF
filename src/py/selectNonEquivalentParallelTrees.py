#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys

for line in sys.stdin:
    line=line.strip()
    parts=line.split("|")
    if len(parts) == 2:
        if parts[0].strip() != parts[1].strip():
            print line
    elif len(parts) >= 4:
        if parts[1].strip() != parts[3].strip():
            print line
    else:
        print line
    
