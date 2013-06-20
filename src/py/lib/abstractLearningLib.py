#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-

import sys, math
from pulp import *
from pickle import OBJ


try:
    import pgf
except ImportError:
    pass

from operator import itemgetter, attrgetter
from collections import namedtuple

class Debugger(object):
    DEBUG = None
    
    @staticmethod
    def debug(message):
        if Debugger.DEBUG:
            print >> sys.stderr, message
    
    @staticmethod
    def set_debug(p_debug):
        Debugger.DEBUG = p_debug
    
    @staticmethod
    def is_debug_enabled():
        return Debugger.DEBUG

def debug(message):
    Debugger.debug(message)
def set_debug(p_debug):
    Debugger.set_debug(p_debug)


class ExtendedBracket(object):
    openCategories = set(["A", "N", "N2", "N3", "PN", "Adv", "V", "V2", "V3", "VS", "V2S", "VV", "V2V", "VA", "V2A", "VQ", "V2Q", "String"])
    
    def __init__(self, bracketObject, parent=None):
        self.parent = parent
        self.bracket = bracketObject
        self.children = list()
        self.leaves = list()
        self.leaf_functions = list()
        self.open_leaf_functions = list()
        self.unsorted_open_leaf_functions = list()
        
        linearisationList = list()
        
        debug("Creating extended bracket with bracket=" + str(bracketObject))

        for i in range(len(self.bracket.children)):
            child = self.bracket.children[i]
            
            if not isinstance(child, basestring):
                self.children.append(ExtendedBracket(child, self))
                linearisationList.append(self.children[-1].linearisation)
            else:
                self.leaves.append(child)
                linearisationList.append(child)
        
        self.linearisation = " ".join(linearisationList)
        
        
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def get_all_subtrees(self):
        outputList = [self]
        if not self.is_leaf():
            for child in self.children:
                outputList += child.get_all_subtrees()
        return outputList
    
    def compute_open_leaf_functions(self):
        self.unsorted_open_leaf_functions = [lf for lf in self.leaf_functions if len(lf.split("_")) > 0 and lf.split("_")[-1] in ExtendedBracket.openCategories ]
        self.open_leaf_functions = sorted(self.unsorted_open_leaf_functions)
    
    def compute_leaf_functions_recursively(self):
        if self.is_leaf():
            if self.bracket.cat == "String":
                self.leaf_functions.append(self.bracket.children[0] + "_String")
            else:
                self.leaf_functions.append(self.bracket.fun)
        else:
            for child in self.children:
                for leaffunction in child.compute_leaf_functions_recursively():
                    self.leaf_functions.append(leaffunction)
        self.compute_open_leaf_functions()
        return self.leaf_functions
    
    def is_alignment_compatible(self, otherTree):
        return not self.is_leaf() and not otherTree.is_leaf() and len(self.open_leaf_functions) >= 1 and len(otherTree.open_leaf_functions) >= 1 and self.bracket.cat == otherTree.bracket.cat and self.open_leaf_functions == otherTree.open_leaf_functions
    
    def is_alignment_compatible_with_bilphrase_list(self, otherTree, bilphrases):
        return   bilphrases.contains_biligual_phrase(self.linearisation,otherTree.linearisation) and not self.is_leaf() and not otherTree.is_leaf() and self.bracket.cat == otherTree.bracket.cat and (len(self.leaf_functions) > 1 or len(otherTree.leaf_functions) > 1)
    
    def is_leaf_alignment_compatible_with_bilphrase_list(self, otherTree, bilphrases):
        return bilphrases.contains_biligual_phrase(self.linearisation,otherTree.linearisation) and self.is_leaf() and otherTree.is_leaf() 
    
    def print_data(self):
        print self.bracket.fun + ":" + self.bracket.cat + " " + str(self.leaf_functions) + " " + str(self.bracket)
        for child in self.children:
            child.print_data()
    
    def __repr__(self):
        return self.bracket.fun + ":" + self.bracket.cat + " " + str(self.leaf_functions) + " " + str(self.open_leaf_functions) + " " + str(self.bracket)
    
    def get_parent_fun_list(self):
        if self.parent == None:
            return []
        else:
            return [self.parent.bracket.fun] + self.parent.get_parent_fun_list()
    
    def get_all_parents(self):
        if self.parent == None:
            return []
        else:
            return [self.parent] + self.parent.get_all_parents()
    
    # deprecated. use get_expr() instead
    def get_function_tree_string(self):
        if self.is_leaf():
            return self.bracket.fun
        else:
            parts = list()
            if len(self.children) == 1:
                parts.append(" ")
                parts.append(self.bracket.fun)
                parts.append(" (")
                parts.append(self.children[0].get_function_tree_string())
                parts.append(")")
            else:
                parts.append(" ")
                parts.append(self.bracket.fun)
                for child in self.children:
                    parts.append(u" (")
                    parts.append(child.get_function_tree_string())
                    parts.append(u")")
            return "".join(parts)
    

class ExtendedExpr(object):
    
    WILDCARD_PREFIX = "wildcard_"
    WILDCARD_IGNORE = "wildcard_IGNORE"
    WILDCARD_SUBTREE_PREFIX = "othermwe_"
    STRING_LEAF_FUN_PREFIX="String_"
    
    def __init__(self, expr, pgfLanguage):
        self.expr = expr
        self.children = list()
        self.leaf_functions = None
        self.open_leaf_functions = None
        self.unsorted_open_leaf_functions = list()
        self.fun = None
        self.cat = None
        self.max_depth = None
        self.list_of_non_leaf_functions = None
        locchildren = []
        
        if not isinstance(expr, basestring):
            unpacked = expr.unpack()
            
            if unpacked != None and not isinstance(unpacked, basestring) and len(unpacked) == 2:
                self.fun = unpacked[0]
                locchildren = unpacked[1]
                if pgfLanguage:
                    try:
                        linearized = pgfLanguage.bracketedLinearize(expr)
                        self.cat = linearized.cat
                    except pgf.PGFError:
                        pass
            else:
                if isinstance(unpacked, basestring):
                    self.fun='"'+unpacked+'"'
                else:
                    self.fun='?'
        else:
            self.fun=expr
        
        for childexpr in locchildren:
            self.children.append(ExtendedExpr(childexpr, pgfLanguage))

    def is_this_fun_wildcard(self):
        return self.fun.startswith("wildcard_")

    def is_leaf(self):
        return len(self.children) == 0
    
    def is_wildcarded_compatible_with(self, exprwithoutwildcards, bindings):
        if self.fun == exprwithoutwildcards.fun:
            if len(self.children) == len(exprwithoutwildcards.children):
                return all(self.children[i].is_wildcarded_compatible_with(exprwithoutwildcards.children[i], bindings) for i in range(len(self.children)))
            else:
                return False
        elif self.is_this_fun_wildcard() and self.is_leaf() and exprwithoutwildcards.is_leaf():
            bindings.append((self.fun, exprwithoutwildcards.fun))
            return True
        else:
            return False
    
    def search_subtree_with(self, fun, open_leaf_functions):
        if self.fun == fun and self.open_leaf_functions == open_leaf_functions:
            return self
        else:
            candidates = [ child.search_subtree_with(fun, open_leaf_functions) for child in self.children ]
            trueCandidates = [candidate for candidate in candidates if candidate != None]
            if len(trueCandidates) > 0:
                return trueCandidates[0]
            else:
                return None

    def compute_max_depth_recursively(self):
        if self.max_depth == None:
            if self.is_leaf():
                self.max_depth = 0
            else:
                self.max_depth = 1 + max([ child.compute_max_depth_recursively() for child in self.children ])
        return self.max_depth
    
    def get_non_leaf_funtions(self):
        if self.list_of_non_leaf_functions == None:
            nonleaffunctions = list()
            if not self.is_leaf():
                nonleaffunctions.append(self.fun)
                for child in self.children:
                    nonleaffunctions.extend(child.get_non_leaf_funtions())
            self.list_of_non_leaf_functions = nonleaffunctions
            
        return self.list_of_non_leaf_functions
    
    def get_wildcard_leaf_functions(self):
        return [f for f in self.get_leaf_functions() if ExtendedExpr.is_par_fun_wildcard(f) ]
    
    def get_non_wildcard_leaf_functions(self):
        return [f for f in self.get_leaf_functions() if  ExtendedExpr.is_par_fun_non_wildcard(f) ]
    
    def get_leaf_functions(self):
        if self.leaf_functions == None:
            self.compute_leaf_functions_recursively()
        return self.leaf_functions
    
    def compute_leaf_functions_recursively(self):
        self.leaf_functions = list()
        if self.is_leaf():
            if self.fun != None:
                self.leaf_functions.append( self.fun if not self.fun.startswith('"') else ExtendedExpr.STRING_LEAF_FUN_PREFIX+self.fun[1:-1])
        else:
            for child in self.children:
                for leaffunction in child.compute_leaf_functions_recursively():
                    self.leaf_functions.append(leaffunction)
        self.compute_open_leaf_functions()
        return self.leaf_functions
    
    def get_open_leaf_functions(self):
        if self.open_leaf_functions == None:
            self.compute_open_leaf_functions()
        return self.open_leaf_functions
    
    def compute_open_leaf_functions(self):
        self.unsorted_open_leaf_functions = [lf for lf in self.get_leaf_functions() if lf and len(lf.split("_")) > 0 and lf.split("_")[-1] in ExtendedBracket.openCategories ]
        self.open_leaf_functions = sorted(self.unsorted_open_leaf_functions)   
    
    def get_all_subtrees(self):
        outputList = [self]
        if not self.is_leaf():
            for child in self.children:
                outputList += child.get_all_subtrees()
        return outputList

    
    def add_refs_to_sub(self,otherexpr,mweset):
        slsubtrees = self.children
        tlsubtrees = otherexpr.children
        
        slfuns = [expr.fun for expr in slsubtrees]
        tlfuns = [expr.fun for expr in tlsubtrees]
        
        candidateReplacements = list()
        for i in range(len(slfuns)):
            slfun = slfuns[i]
            for j in range(len(tlfuns)):
                tlfun = tlfuns[j]
                candidates = mweset.get_mwes_for_funs(slfun, tlfun)
                if len(candidates) > 0:
                    candidateReplacements.append((i, j, candidates))
        
        # Simply pick first candidate replacement. TODO: find the optimum 
        for i, j, mwes in candidateReplacements:
            bilExpr = BilingualExpr()
            bilExpr.set_exprs(slsubtrees[i], tlsubtrees[j])
            for mwe in mwes:
                if mwe.is_bilexpr_matched_or_reproduced(bilExpr).reproduced:
                    self.replace_subtree_with_MWE_ref(i, mwe.id)
                    otherexpr.replace_subtree_with_MWE_ref(j, mwe.id)
        
        # do the same with subtrees
        #really conservative approach: only if the amount of children is the same
        #and they share function
        if len(slsubtrees) == len(tlsubtrees):
            for i in range(len(slsubtrees)):
                slsubtree=slsubtrees[i]
                tlsubtree=tlsubtrees[i]
                if not slsubtree.is_leaf() and not tlsubtree.is_leaf(): 
                    if slsubtree.fun == tlsubtree.fun:
                        slsubtree.add_refs_to_sub(tlsubtree,mweset)
                    
    
    def replace_subtree_with_MWE_ref(self, subtreeindex, mweid=0):
        self.children[subtreeindex]=ExtendedExpr(pgf.readExpr(ExtendedExpr.WILDCARD_SUBTREE_PREFIX+str(mweid)),None)
    
    def str_with_generalised_functions(self, functionsToGeneralise):
        
        # replace non-content leaf functions with special wildcard
        nonContentLeafFunctions = [ fun for fun in self.leaf_functions if not '_' in fun]
        
        # create dictionary with leaf functions and variable names
        variablesDict = dict()
        for fun in nonContentLeafFunctions:
            variablesDict[fun] = ExtendedExpr.WILDCARD_IGNORE
        wildcardindex = 1
        for funl in functionsToGeneralise:
            for fun in funl:
                variablesDict[fun] = ExtendedExpr.WILDCARD_PREFIX + str(wildcardindex)
            wildcardindex += 1
        
        # replace them
        exprstr = str(self.expr)
        
        debug("Generalising functions of '" + exprstr + "' with generalised functions " + str(functionsToGeneralise))
        
        return reduce(lambda a, kv: a.replace(*kv), variablesDict.iteritems(), exprstr)
    
    def __repr__(self):
        # return self.fun+":"+str(self.cat)+" "+str(self.leaf_functions)+" "+str(self.open_leaf_functions)+" "+str(self.expr)
        #return str(self.expr)
        if self.is_leaf():
            return self.fun
        else:
            childrenstr=[str(child) for child in self.children]
            return " ".join( ["(",self.fun]+childrenstr+[")"] )
   
    
    def str_with_variables(self, openLeafFunctions=None):
        categoriesCounter = dict()
        for cat in ExtendedBracket.openCategories:
            categoriesCounter[cat] = 0
        
        # create dictionary with leaf functions and variable names
        variablesDict = dict()
        myOpenLeafFunctions = openLeafFunctions if openLeafFunctions else self.unsorted_open_leaf_functions
        for leaf in myOpenLeafFunctions:
            cat = leaf.split("_")[-1]
            var = cat + str(categoriesCounter[cat])
            variablesDict[leaf] = var
            categoriesCounter[cat] = categoriesCounter[cat] + 1
        
        # replace them
        exprstr = str(self.expr)
        return reduce(lambda a, kv: a.replace(*kv), variablesDict.iteritems(), exprstr)
    
    
    def str_with_children_cat(self, extendedbracket):
        
        # create dictionary with children fun names and cats
        funCatDict = dict()
        for child in extendedbracket.children:
            funCatDict[child.bracket.fun] = child.bracket.cat
        
        # return fun name and cats of children
        return self.fun + " " + " ".join([ str(funCatDict.get(c.fun)) for c in self.children ])
        
        
    @staticmethod
    def is_par_fun_wildcard(fun):
        return fun.startswith(ExtendedExpr.WILDCARD_PREFIX) and not fun.startswith(ExtendedExpr.WILDCARD_IGNORE)

    @staticmethod
    def is_par_fun_non_wildcard(fun):
        return not fun.startswith(ExtendedExpr.WILDCARD_PREFIX) and not fun.startswith(ExtendedExpr.WILDCARD_IGNORE)

class AbstractBilingualExpr(object):
    def __init__(self):
        self.freq = 0
        self.slexpr = None
        self.tlexpr = None
    
    def set_exprs(self, p_slexpr, p_tlexpr):
        self.slexpr = p_slexpr
        self.tlexpr = p_tlexpr
    
    def parse(self, rawstr, ignoreFreq=False):
        parts = rawstr.split(" | ")
        offset = -1
        if not ignoreFreq:
            self.freq = int(parts[0])
            offset = 0
        self.slexpr = ExtendedExpr(pgf.readExpr(parts[1 + offset]), None)
        self.slexpr.compute_leaf_functions_recursively()
        self.tlexpr = ExtendedExpr(pgf.readExpr(parts[2 + offset]), None)
        self.tlexpr.compute_leaf_functions_recursively()
    
    #TODO: ¿mejorar con dic. bilingüe?
    def is_equal_sides(self):
        return str(self.slexpr) == str(self.tlexpr)
    
    def __repr__(self):
        output = str(self.slexpr) + " | " + str(self.tlexpr)
        if self.freq > 0:
            output = str(self.freq) + " | " + output
        return output

class BilingualExpr(AbstractBilingualExpr):
    
    def extract_candidate_mwes(self):
        slleafs = [ fun for fun in self.slexpr.get_leaf_functions() if '_' in fun ] 
        tlleafs = [ fun for fun in self.tlexpr.get_leaf_functions() if '_' in fun ]
        
        debug("sl leaf functions: " + str(slleafs))
        
        returnList = list()
        # alignedLeafFuns=[ slleaf for slleaf in slleafs if slleaf in tlleafs ]
        
        leafFunPairs = list()
        FunsWithWildcards = namedtuple('FunsWithWildcards', ['sl', 'tl'])
        for leaf in slleafs:
            tlalternatives = list()
            if leaf in tlleafs:
                tlalternatives.append(leaf)
            if leaf in ParallelMWE.synonymDict:
                for syn in ParallelMWE.synonymDict[leaf]:
                    if syn in tlleafs:
                        tlalternatives.append(syn)
            
            if len(tlalternatives) > 0:
                leafFunPairs.append(FunsWithWildcards(leaf, tlalternatives))
        
        for subAlignedLeafFuns in powerset(leafFunPairs):
            returnList.append(self.to_parallel_mwe_str(subAlignedLeafFuns))
        
        return returnList
    
    def to_parallel_mwe_str(self, functionsToGeneralise):
            return str(self.slexpr.get_non_leaf_funtions()) + " | " + str(self.tlexpr.get_non_leaf_funtions()) + " | " + self.slexpr.str_with_generalised_functions([ [fs.sl] for fs in functionsToGeneralise]) + " | " + self.tlexpr.str_with_generalised_functions([ fs.tl for fs in functionsToGeneralise])


class ParallelMWESet(object):
    
    def __init__(self):
        self.index = dict()
        self.idcounter = 0
    
    def add(self, mwe):
        self.idcounter += 1
        mwe.id = self.idcounter
        if not mwe.slexpr.fun in self.index:
            self.index[mwe.slexpr.fun] = dict()
        secondleveldict = self.index[mwe.slexpr.fun]
        if not mwe.tlexpr.fun in secondleveldict:
            secondleveldict[mwe.tlexpr.fun] = list()
        secondleveldict[mwe.tlexpr.fun].append(mwe)
        
    def get_mwes_for_funs(self, slfun, tlfun):
        mwes = list()
        if slfun in self.index:
            if tlfun in self.index[slfun]:
                mwes = self.index[slfun][tlfun]  
        return mwes
    

class ParallelMWE(AbstractBilingualExpr):
    
    synonymDict = dict()
    
    def __init__(self):
        self.bilExprsReproduced = set()
        self.bilExprsMatched = set()
        self.totalBilExprsReproduced = 0
        self.totalBilExprsMatched = 0
        self.id = 0
        super(ParallelMWE, self).__init__()
    
    def get_representative(self):
        return self.slexpr.get_non_leaf_funtions()
    
    def get_proportion_reproduced(self):
        if self.totalBilExprsMatched > 0:
            return self.totalBilExprsReproduced * 1.0 / self.totalBilExprsMatched
        else:
            return 0
        
    def get_total_wildcards(self):
        return len(self.slexpr.get_wildcard_leaf_functions())
    
    def parse(self, rawstr):
        super(ParallelMWE, self).parse(rawstr, True)
    
    # maybe this is too greedy
    def add_refs_to_sub(self, mweset):
        self.slexpr.add_refs_to_sub(self.tlexpr,mweset)
        
    
    def is_bilexpr_matched_or_reproduced(self, bilingualExpr):
        
        MatchedReproduced = namedtuple('MatchedReproduced', ['matched', 'reproduced'])
        MatchedReproduced(False, False)
        matched = False
        reproduced = False
        
        # debug("checking whether "+str(bilingualExpr)+" is reproduced by "+str(self))
        
        # check structure
        slbindings = list()
        tlbindings = list()
        isSLReproducible = self.slexpr.is_wildcarded_compatible_with(bilingualExpr.slexpr, slbindings)
        isTLReproducible = False
        if isSLReproducible:
            matched = True
            isTLReproducible = self.tlexpr.is_wildcarded_compatible_with(bilingualExpr.tlexpr, tlbindings)
        
        if not isSLReproducible or not isTLReproducible:
            # debug("NO: Different structure")
            return MatchedReproduced(matched, reproduced)
        
        # check whether variables are compatible
        bindingDict = dict()
        for binding in slbindings:
            if not binding[0] in bindingDict.keys():
                bindingDict[binding[0]] = set()
            bindingDict[binding[0]].add(binding[1])
        
        for binding in tlbindings:
            if not binding[0] in bindingDict.keys():
                bindingDict[binding[0]] = set()
            if not binding[1] in bindingDict[binding[0]]:
                # check if is synonym of any word already present
                isSynonym = False 
                for slbinded in bindingDict[binding[0]]:
                    if slbinded in ParallelMWE.synonymDict:
                        if binding[1] in ParallelMWE.synonymDict[slbinded]:
                            isSynonym = True
                if not isSynonym:
                    bindingDict[binding[0]].add(binding[1])

        # each wildcard must have a single value
        wildcardTest = all(len(bindingDict[key]) <= 1 for key in  bindingDict.keys() if key != ExtendedExpr.WILDCARD_IGNORE)
        
        # if not wildcardTest:
            # debug("NO: Incompatible variables")
        # else:
            # debug("YES")
        
        return MatchedReproduced(matched, wildcardTest)
    
    def compute_reproduced_and_matching_bilexprs(self, bilexprs):
        for i in range(len(bilexprs)):
            result = self.is_bilexpr_matched_or_reproduced(bilexprs[i])
            if result.reproduced:
                self.bilExprsReproduced.add(i)
                self.totalBilExprsReproduced += bilexprs[i].freq
            if result.matched:
                self.bilExprsMatched.add(i)
                self.totalBilExprsMatched += bilexprs[i].freq
    
    def __repr__(self):
        baserepr=super(ParallelMWE, self).__repr__()
        if self.totalBilExprsMatched > 0 or self.totalBilExprsReproduced > 0:
            return str(self.totalBilExprsReproduced)+" | "+str(self.get_proportion_reproduced())+" | "+baserepr
        else:
            return baserepr

class MWEReader(object):
    
    s_bilingualexprs = None
    s_groups = list()
    
    @classmethod
    def process(cls,mygroup):
        basefunl = mygroup[0].get_representative()
        
        bilingualExprs =None
        if cls.s_bilingualexprs:
            bilingualExprs = [b for b in cls.s_bilingualexprs if b.slexpr.get_non_leaf_funtions() == basefunl]

        cls.s_groups.append((mygroup, bilingualExprs))

class MWESplitter(object):
    def __init__(self,p_groupsdir):
        self.id=0
        self.groupsdir=p_groupsdir
    
    def process(self,mygroup):
        self.id+=1
        myfile=open(self.groupsdir+"/"+str(self.id),'w')
        for mwe in mygroup:
            myfile.write(str(mwe)+"\n")
        myfile.close()


def select_mwes(mwesplusbils, threshold=2, minPropReproduced=0.0):
    mygroup = mwesplusbils[0]
    bilingualExprs = mwesplusbils[1]

    # compute bilingual exprs reproduced by each mwe
    for mwe in mygroup:
        mwe.compute_reproduced_and_matching_bilexprs(bilingualExprs)
        
        # debug results
        if Debugger.DEBUG:
            debug("Biligual expressions reproduced by mwe: " + str(mwe) + " :")
            for i in mwe.bilExprsReproduced :
                debug("\t" + str(bilingualExprs[i]))
    
    debug("MWEs and their scores")
    for mwe in mygroup:
        debug(str(mwe)+" prop:"+str(mwe.get_proportion_reproduced())+"% freq: "+str(mwe.totalBilExprsReproduced))
    
    # discard mwes which do not reproduce at least two bilingual exprs
    reliableMwes = [mwe for mwe in mygroup if mwe.totalBilExprsReproduced >= threshold and mwe.get_proportion_reproduced() >= minPropReproduced]
    idcounter = 1
    for mwe in reliableMwes:
        mwe.id = idcounter
        idcounter += 1
      
    # compute mwes which reproduce each bilingual expr
    mwesReproducingEachBil = [ [] for bil in bilingualExprs ]
    for mwe in reliableMwes:
        for bindex in mwe.bilExprsReproduced:
            mwesReproducingEachBil[bindex].append(mwe.id)
    
    if Debugger.is_debug_enabled():
        for i in range(len(bilingualExprs)):
            bilexpr = bilingualExprs[i]
            debug("MWEs correctly reproducing bil expr " + str(bilexpr))
            if len(mwesReproducingEachBil[i]) == 0:
                debug("\tNone")
            for mweid in mwesReproducingEachBil[i]:
                debug("\t" + str(reliableMwes[mweid - 1]))          
    
    # we need the number of wildcards of each AT
    totalWildcards = sum(mwe.get_total_wildcards() for mwe in reliableMwes)
    
    
    # build minimisation problem
    prob = LpProblem("Mwes", LpMinimize)
    # variables
    lp_variables = dict()
    for mwe in reliableMwes:
        var = LpVariable("x" + str(mwe.id), 0, 1, cat='Integer')
        lp_variables[mwe.id] = (var, totalWildcards + mwe.get_total_wildcards())
    
    # restriction: each bilexpr must be reproduced by at least one mwe in the solution
    for i in range(len(mwesReproducingEachBil)):
        mwesReproducingMe = mwesReproducingEachBil[i]
        if len(mwesReproducingMe) > 0:
            cname = "bilexpr" + str(i)
            myexpression = LpAffineExpression([ (lp_variables[mweid][0], 1) for mweid in mwesReproducingMe ])
            constraint = LpConstraint(myexpression, sense=constants.LpConstraintGE, name=cname, rhs=1)
            # prob += lpSum([ (lp_variables[vari],1) for vari in var_ids ]) >= 1 , cname 
            prob.constraints[cname] = constraint  
    
    # expression to be minimised: number of mwes
    myexpression = LpAffineExpression([ var for var in lp_variables.values() ])
    prob.objective = myexpression
    
    status = prob.solve()
    solution = list()
    if status == LpStatusOptimal :
        
        for vid in lp_variables.keys():
                if value(lp_variables[vid][0]) == 1:
                        solution.append(reliableMwes[vid - 1])
    else:
        print >> sys.stderr, str(mygroup[0].get_representative()) + " status: " + str(LpStatus[status])
        
    return solution

class ExprNotFoundException(Exception):
    def __init__(self, blame):
        self.blame = blame

class Alignment(object):
    def __init__(self, slbracket, slfullexpr, tlbracket, tlfullexpr):
        self.slbracket = slbracket
        self.tlbracket = tlbracket
        
        self.slparentfun = self.slbracket.get_parent_fun_list()
        self.tlparentfun = self.tlbracket.get_parent_fun_list()
        
        self.slexpr = slfullexpr.search_subtree_with(slbracket.bracket.fun, slbracket.open_leaf_functions)
        self.tlexpr = tlfullexpr.search_subtree_with(tlbracket.bracket.fun, tlbracket.open_leaf_functions)
        if not self.slexpr or not self.tlexpr:
            blame = ""
            if not self.slexpr:
                blame += (" SL" + str(self.slbracket))
            if not self.tlexpr:
                blame += (" TL" + str(self.tlbracket))
            raise ExprNotFoundException(blame)
    
    def to_string(self, onlyChildrenCats=False):
        if onlyChildrenCats:
            return (self.slparentfun[0] if len(self.slparentfun) > 0 else "_") + " | " + self.slexpr.str_with_children_cat(self.slbracket) + " | " + (self.tlparentfun[0] if len(self.tlparentfun) > 0 else "_") + " | " + self.tlexpr.str_with_children_cat(self.tlbracket)
        else:
            # return (self.slparentfun[0] if len(self.slparentfun)  > 0 else "_") + " | " + self.slexpr.str_with_variables()+ " | " + (self.tlparentfun[0] if len(self.tlparentfun)  > 0 else "_") + " | " + self.tlexpr.str_with_variables(self.slexpr.unsorted_open_leaf_functions)
            return (self.slparentfun[0] if len(self.slparentfun) > 0 else "_") + " | " + str(self.slexpr.expr) + " | " + (self.tlparentfun[0] if len(self.tlparentfun) > 0 else "_") + " | " + str(self.tlexpr.expr)
    
    def __repr__(self):
        return self.to_string()


class BilingualPhraseSet(object):
    
    def __init__(self):
        self.bilingualPhrases=set()
    
    def add(self,rawbilentry,addOneToOne=True):
        parts=rawbilentry.split("|||")
        self.bilingualPhrases.add("|||".join(parts[:2]).strip())
        if addOneToOne:
            slwords=parts[0].strip().split(" ")
            tlwords=parts[1].strip().split(" ")
            alignmentsstrparts=parts[2].strip().split(" ")
            for alstr in alignmentsstrparts:
                slandtlstr= alstr.split("-")
                slindex=int(slandtlstr[0])
                tlindex=int(slandtlstr[1])
                self.bilingualPhrases.add(slwords[slindex]+" ||| "+tlwords[tlindex])
    
    def contains_biligual_phrase(self,slphrase,tlphrase):
        return slphrase+" ||| "+tlphrase in self.bilingualPhrases
        

class GFProbabilisticBilingualDictionary(object):
    def __init__(self):
        self.dict = dict()
    
    def extract_entries_from_aligned_trees(self, sourceList, targetList, bilingualPhrases,invert=False):
        for sourceTree in sourceList:
            for targetTree in targetList:
                if sourceTree.is_leaf_alignment_compatible_with_bilphrase_list(targetTree, bilingualPhrases):
                    if invert:
                        self.increase_pair(targetTree.bracket.fun, sourceTree.bracket.fun)
                    else:
                        self.increase_pair(sourceTree.bracket.fun, targetTree.bracket.fun)
    
    def increase_pair(self, slfun, tlfun):
        if slfun != "" and tlfun != "":
            if not slfun in self.dict.keys():
                self.dict[slfun] = dict()
            if not tlfun in self.dict[slfun].keys():
                self.dict[slfun][tlfun] = 0
            self.dict[slfun][tlfun] = self.dict[slfun][tlfun] + 1
    
    def write(self, fobject):
        for pair in self.dict.iteritems():
            fobject.write(pair[0] + "\n")
            targetfreqpairsorted = sorted(pair[1].iteritems(), key=lambda a: a[1] , reverse=True)
            for targetfreq in targetfreqpairsorted:
                fobject.write("\t" + str(targetfreq[1]) + "\t" + targetfreq[0] + "\n")
    
    def read(self, fobject):
        PairTabReader.process(self, fobject)
    
    def process(self, funpairsobj):
        slfun = funpairsobj.get_leftFun().fun
        self.dict[slfun] = dict()
        for ffp in funpairsobj.get_rightFuns():
            self.dict[slfun][ffp.fun] = ffp.freq
    
    def generate_synonim_dict(self):
        synonymDict = dict()
        for slfun in self.dict.keys():
            synonymDict[slfun] = set()
            tlfunsdict = self.dict[slfun]
            threshold = 1
            if slfun in tlfunsdict:
                threshold = tlfunsdict[slfun]
            
            # include in the synonim list words
            # with freq higher or equal than the GF translation
            for keyvalue in tlfunsdict.iteritems():
                if keyvalue[1] >= threshold:
                    synonymDict[slfun].add(keyvalue[0])
        return synonymDict    
        

class FunFreqPair(object):
    def __init__(self, fun=None, freq=0):
        self.fun = fun
        self.freq = freq
    
    def parse(self, rawstr):
        if "|" in rawstr:
            parts = rawstr.split(" | ")
        else:
            parts = rawstr.strip().split("\t")
        if len(parts) == 1:
            self.freq = 0
            self.fun = parts[0]
        else:
            numbers = parts[0].strip().split(" ")
            self.freq = int(numbers[0])
            self.fun = parts[1].strip()
        


class FunPairs(object):
    def __init__(self):
        self.leftFun = None
        self.rightFuns = list()
    
    def set_leftFun(self, p_leftFun):
        self.leftFun = p_leftFun
    
    def get_leftFun(self):
        return self.leftFun
    
    def add_rightFun(self, p_ffp):
        self.rightFuns.append(p_ffp)
    
    def get_rightFuns(self):
        return self.rightFuns
    
    def is_empty(self):
        return self.leftFun == None
    
    


class PairTabReader(object):
    @staticmethod
    def read_group(mybuffer, inputF):
        funPairs = FunPairs()
        if len(mybuffer) > 0:
            rawline = mybuffer[0]
        else:
            rawline = inputF.readline()
        
        if len(rawline) > 0:
            ffp = FunFreqPair()
            ffp.parse(rawline)
            funPairs.set_leftFun(ffp)
            
            rawline = inputF.readline()
            while rawline.startswith("\t"):
                ffp = FunFreqPair()
                ffp.parse(rawline)
                funPairs.add_rightFun(ffp)
                
                rawline = inputF.readline()   
        
        mybuffer[:] = []
        if len(rawline) > 0:
            mybuffer.append(rawline)
        
        return funPairs
    
    @staticmethod
    def process(groupProcessorClass, inputF=sys.stdin):
        mybuffer = list()
        mygroup = PairTabReader.read_group(mybuffer, inputF)
        while not mygroup.is_empty():
            groupProcessorClass.process(mygroup)
            mygroup = PairTabReader.read_group(mybuffer, inputF)

    
class Model1Processor(object):
    
    numExamplesProcessed = 0
    numExamplesReproduced = 0
    
    MINIMUM_DIFFERENCE = 0.5
    
    @staticmethod
    def process(funPairs):
        
        # check entropy
        # entropy=calc_entropy([ rightfun.freq*1.0/funPairs.leftFun.freq for rightfun in funPairs.rightFuns])
        
        # simply choose the most frequent translation
        sortedRights = sorted(funPairs.rightFuns, key=attrgetter('freq'), reverse=True)
        
        # check whether the first option is significantly most frequent than the second one
        if len(sortedRights) == 1 or sortedRights[0].freq * 1.0 / funPairs.leftFun.freq - sortedRights[1].freq * 1.0 / funPairs.leftFun.freq >= Model1Processor.MINIMUM_DIFFERENCE:
            print str(funPairs.leftFun.freq) + " " + str(sortedRights[0].freq * 1.0 / funPairs.leftFun.freq) + " | " + funPairs.leftFun.fun + " | " + sortedRights[0].fun
            Model1Processor.numExamplesReproduced += sortedRights[0].freq
        
        Model1Processor.numExamplesProcessed += funPairs.leftFun.freq


def calc_entropy(freqList):
    ent = 0.0
    for freq in freqList:
        ent = ent + freq * math.log(freq, 2)
    ent = -ent
    return ent

def split_partial_parse(line):
    trees = list()
    if line.startswith("?"):
        # partial parse. Do stuff
        myline = line[1:].strip()
        while len(myline) > 0:
            if myline.startswith("("):
                # find position of matching parenthesis
                stack = list()
                stack.append("(")
                pos = 1
                while len(stack) > 0 and pos < len(myline):
                    char = myline[pos]
                    if char == "(":
                        stack.append(")")
                    elif char == ")":
                        stack.pop()
                    pos += 1
                if len(stack) == 0:
                    trees.append(myline[:pos].strip())
                    myline = myline[pos:].strip()
                else:
                    # ugly error. print the whole line
                    trees.append(myline)
                    myline = ""
                
            else:
                # find first whitespace
                endpos = myline.find(" ")
                if endpos == -1:
                    endpos = len(myline)
                trees.append(myline[:endpos])
                myline = myline[endpos:].strip()
    else:
        trees.append(line)
    return trees


def powerset(seq):
    """
    Returns all the subsets of this set. This is a generator.
    """
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]] + item
            yield item
