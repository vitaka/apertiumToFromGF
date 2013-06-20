'''
Created on 28/05/2013

@author: vitaka
'''
import sys

def uniprint(unicodestr,erroutput=False,encoding='utf-8'):
    if erroutput:
        print >> sys.stderr, unicodestr.encode(encoding)
    else:
        print unicodestr.encode(encoding)
def unidecode(rawstr,encoding='utf-8'):
    return rawstr.decode(encoding)