'''
Created on 28/05/2013

@author: vitaka
'''
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chooses alignment templates.')
    parser.add_argument("--min_prop_reproduced",default="0.7")
    args = parser.parse_args(sys.argv[1:])
    
    minprop=float(args.min_prop_reproduced)
    
    for line in sys.stdin:
        parts=line.split(" | ")
        proprepr=float(parts[1])
        if proprepr >= minprop:
            print parts[2].strip()+" | "+parts[3].strip()
    