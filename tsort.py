"""~    @h2{tsort.py}   
    topological sort orders a directed acyclic graph,
    in order to make sure nodes are only visited after
    all their required nodes have been visited.

@i{listing prepared with lpy.py}@N

"""

__Copyright__ = """
    Copyright (c) 2004 Dirck Blaskey

    Permission is granted to use this source for any purpose,
        provided that this notice remains.
    
    This software is provided 'as is' without express or implied warranty, 
        and with no claim as to its suitability for any purpose.
        
    (No lifeguard on duty, use at your own risk.)

    for more information, contact:
        Danbala Software
        http://www.danbala.com
"""

#~Last Modified:

__Id__="$Id: tsort.py.txt,v 1.1 2005/02/02 06:32:35 u37519820 Exp $"

'''~    @h3{tsort(arcs) - topological sort}
    arcs is a list of pairs [(r,s), (r,s)]
    values in the pairs are any dictionary-keyable type
    
    returns the ordered list or 
        raises "loop detected", (item, output[], remainder[])
'''    
def tsort(arcs):
    
    """~
nodes is a dictionary of list[2]
    [0] is requirement count
    [1] is supports list

using a class might be slightly more readable        

build the nodes from the graph description:"""
    
    nodes = {}
    for left, right in arcs:        
        # add the successor node to predecessor's supports list
        t = nodes.get(left, None)
        if not t:
            nodes[left] = [0,[right]]
        else:
            t[1].append(right)
        
        # add the predecessor node to successor's requirements count
        t = nodes.get(right, None)
        if not t:
            nodes[right] = [1,[]]
        else:
            t[0] = t[0] + 1

    #~ nodes is ready, get the keys and prep the output list
        
    keys   = nodes.keys() # get the nodes list
    nItems = len(keys)    # number of nodes
    out    = [0]*nItems   # output list
    outp   = 0            # output point
    lo     = 0            # calculation point
    
    """~
for all the keys
    set the number of requirements left
    find any with no requirements
        mark them done and add them to the output list"""
  
    for k in keys:
        t = nodes[k]        # t: [req count, sup list]
        if not t[0]:        # no requirements
            out[outp] = k   # add to output list
            outp = outp + 1

    """~
while there are unprocessed items in the output list
    pull the list of supported items from 
        the next node on the input side of the output list
    release 1 requirement from all the supported items"""
    
    while lo < outp:
        sups = nodes[out[lo]][1]
        lo = lo + 1        
        for k in sups:
            t = nodes[k]
            c = t[0] - 1
            t[0] = c
            # no more requirements on supported item, 
            #   add it to the output list
            if not c:
                out[outp] = k
                outp = outp + 1
    
    #~ if we output all the items, there is no loop, everything is ok
    
    if outp == nItems:
        return out
    
    """~
loop detected - try to locate the loop.
    find the first item with minimum nLeft, 
    and report that as the loop: """
    
    min = 0
    item = 0
    remainder = []
    for k in keys:
        n = nodes[k][0]
        if n > 0:
            remainder.append(k)
            if not min or n < min:
                min = n
                item = k
    
    raise "Loop Detected", (item, out[:outp], remainder)

#--------------------------------------------------------------

#~@h3{test()} test tsort, once without a loop, once with

def test():    
    list = [ ('a','b'), ('c','d'), ('a','f'), 
             ('f','c'), ('c','i'), ('d','b') ]
    
    # a correct order is ['a', 'f', 'c', 'd', 'i', 'b']
    #  but the order could be arbitrary: dictionary.keys() isn't ordered
    print "1: Expecting ['a', 'f', 'c', 'd', 'i', 'b'] (or similar):"
    print tsort(list)
    print
        
    list = [ ('a','b'), ('c','d'), ('a','f'), 
             ('f','c'), ('b','c'), ('d','b') ]
    # loop : b c, c d, d b
    print "2: Expecting a loop at ('c', ['a', 'f'], ['c', 'b', 'd']):"
    print tsort(list)

# kick it off

if __name__ == "__main__":
    test()       
