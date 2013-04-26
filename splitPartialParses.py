#!/usr/bin/env python

import sys

if __name__ == "__main__":
    for line in sys.stdin:
        line=line.strip()
        if line.startswith("?"):
            #partial parse. Do stuff
            
            myline=line[1:].strip()
            while len(myline) > 0:
                if myline.startswith("("):
                    #find position of matching parenthesis
                    stack=list()
                    stack.append("(")
                    pos=1
                    while len(stack) > 0 and pos < len(myline):
                        char=myline[pos]
                        if char == "(":
                            stack.append(")")
                        elif char== ")":
                            stack.pop()
                        pos+=1
                    if len(stack) == 0:
                        print myline[:pos].strip()
                        myline=myline[pos:].strip()
                    else:
                        #ugly error. print the whole line
                        print myline
                        myline=""
                    
                else:
                    #find first whitespace
                    endpos=myline.find(" ")
                    if endpos == -1:
                        endpos=len(myline)
                    print myline[:endpos]
                    myline=myline[endpos:].strip()    
        else:
            print line
    