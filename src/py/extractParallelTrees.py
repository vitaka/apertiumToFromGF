#!/usr/bin/env python
# coding=utf-8
# -*- encoding: utf-8 -*-


import sys,argparse,lib
from lib.abstractLearningLib import ExtendedBracket, ExtendedExpr, debug, ExprNotFoundException, Alignment, split_partial_parse,GFProbabilisticBilingualDictionary,\
    set_debug,Debugger, BilingualPhraseSet
from operator import itemgetter

try:
    import pgf
except ImportError:
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chooses alignment templates.')
    parser.add_argument('--source_pgf',required=True)
    parser.add_argument('--target_pgf',required=True)
    parser.add_argument('--with_bilingual_phrases',action='store_true')
    parser.add_argument('--create_bilingual_dictionary')
    parser.add_argument('--only_count_parsed_words',action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    set_debug(args.debug)
    DEBUG=Debugger.is_debug_enabled()
        
    bilingualDictionary=GFProbabilisticBilingualDictionary()
    bilingualDictionaryInv=GFProbabilisticBilingualDictionary()
    
    sourcePGF=pgf.readPGF(args.source_pgf)
    sourceLanguage=list(sourcePGF.languages.keys())[0]
    
    targetPGF=pgf.readPGF(args.target_pgf)
    targetLanguage=list(targetPGF.languages.keys())[0]
    
    #option1: search for parallel trees in expr tree enriched with category
    # of linearization on each node. Some nodes have missing category
    
    #option2: search for parallel trees in bracketed tree. Problem:
    #difficult to obtain which part of original expression matched the tree
    #solution: ¿fun + leaf nodes from open categories?
    
    for line in sys.stdin:
        parts=line.split("~")
        sourcePart=parts[0]
        targetPart=parts[1]
        
        bilingualPhrases=BilingualPhraseSet()
        if args.with_bilingual_phrases:
            bilingualPhraseList=parts[2]
            for bil in bilingualPhraseList.split("\t"):
                bilingualPhrases.add(bil.strip())
        
        sourceTreesRaw=split_partial_parse(sourcePart)
        targetTreesRaw=split_partial_parse(targetPart)
        #targetTreesRaw=[]
        
        if DEBUG:
            print >> sys.stderr, "source trees:"
            for t in sourceTreesRaw:
                print >> sys.stderr, t
            print >> sys.stderr, "target trees:"
            for t in targetTreesRaw:
                print >> sys.stderr, t
            
        sourceExprs=[]
        for rawTree in sourceTreesRaw:
            try:
                ### ignore non ascii data ####
                rawTree.decode('ascii')
                expr=pgf.readExpr(rawTree)
                sourceExprs.append(expr)
            except (pgf.PGFError,UnicodeDecodeError):
                print >> sys.stderr, "Could not parse SL expr: "+rawTree
        
        targetExprs=[]
        for rawTree in targetTreesRaw:
            try:
                ### ignore non ascii data ####
                rawTree.decode('ascii')
                expr=pgf.readExpr(rawTree)
                targetExprs.append(expr)
            except (pgf.PGFError,UnicodeDecodeError):
                print >> sys.stderr, "Could not parse TL expr: "+rawTree
        
        debug("checking which exprs can be linearized SL")
        sourceNotCrashingExprs=[ myexpr for myexpr in  sourceExprs if len(sourcePGF.languages[sourceLanguage].linearize(myexpr).strip()) > 0 ]
        debug("checking which exprs can be linearized TL")
        targetNotCrashingExprs=[ myexpr for myexpr in  targetExprs if len(targetPGF.languages[targetLanguage].linearize(myexpr).strip()) > 0 ]
        
        #sourceExtendedExprs=[ ExtendedExpr(myexpr,sourcePGF.languages[sourceLanguage]) for myexpr in  sourceNotCrashingExprs ]
        #targetExtendedExprs=[ ExtendedExpr(myexpr,targetPGF.languages[targetLanguage]) for myexpr in  targetNotCrashingExprs ]
        
        sourceSimpleExtendedExprs=[ ExtendedExpr(myexpr,None) for myexpr in  sourceNotCrashingExprs ]
        targetSimpleExtendedExprs=[ ExtendedExpr(myexpr,None) for myexpr in  targetNotCrashingExprs ]
        
        debug("Creating SL brackets")
        sourceBrackTrees=[ ExtendedBracket(sourcePGF.languages[sourceLanguage].bracketedLinearize(myexpr)) for myexpr in sourceNotCrashingExprs ]
        debug("Creating TL brackets")
        targetBrackTrees=[ ExtendedBracket(targetPGF.languages[targetLanguage].bracketedLinearize(myexpr)) for myexpr in targetNotCrashingExprs ]
        
        for sbt in sourceBrackTrees:
            debug("computing leaf functions for: "+str(sbt))
            sbt.compute_leaf_functions_recursively()
            
        for tbt in targetBrackTrees:
            debug("computing leaf functions for: "+str(tbt))
            tbt.compute_leaf_functions_recursively()
            
        for sbt in sourceSimpleExtendedExprs:
            debug("computing leaf functions for: "+str(sbt))
            sbt.compute_leaf_functions_recursively()
            
        
        for tbt in targetSimpleExtendedExprs:
            debug("computing leaf functions for: "+str(tbt))
            tbt.compute_leaf_functions_recursively()
        
        if args.only_count_parsed_words:
            slparsedwords=" ".join(bt.linearisation for bt in sourceBrackTrees)
            tlparsedwords=" ".join(bt.linearisation for bt in targetBrackTrees)
            print slparsedwords+"|"+tlparsedwords
            continue
        
        #Aligned trees: same words of open lexical categories, same category,  at least two words
        #try to align subtrees with the same category and words from open lexical categories
        sourceList=[]
        for i in range(len(sourceBrackTrees)):
            sbt=sourceBrackTrees[i]
            sourceList+= [ (subtree,i) for subtree in sbt.get_all_subtrees() ]
        targetList=[]
        for i in range(len(targetBrackTrees)):
            tbt=targetBrackTrees[i]
            targetList+=[ (subtree,i) for subtree in tbt.get_all_subtrees()]
        
        if DEBUG:
            print >> sys.stderr, "Source list:"
            for sourceTree in sourceList:
                print >> sys.stderr, sourceTree[0]
            print >> sys.stderr, "Target list:"
            for targetTree in targetList:
                print >> sys.stderr, targetTree[0]
        
        if args.with_bilingual_phrases and args.create_bilingual_dictionary:
            #create a probabilistic bilingual dictionary of GF leaf functions
            bilingualDictionary.extract_entries_from_aligned_trees([ t[0] for t in sourceList],[ t[0] for t in targetList],bilingualPhrases)
            bilingualDictionaryInv.extract_entries_from_aligned_trees([ t[0] for t in sourceList],[ t[0] for t in targetList],bilingualPhrases,invert=True)
        
        initialAlignments=list()
        for sourceTree in sourceList:
            if args.with_bilingual_phrases:
                initialAlignments+=[ (sourceTree,targetTree) for targetTree in targetList if sourceTree[0].is_alignment_compatible_with_bilphrase_list(targetTree[0],bilingualPhrases) ]
            else:
                initialAlignments+=[ (sourceTree,targetTree) for targetTree in targetList if sourceTree[0].is_alignment_compatible(targetTree[0]) ]
        
        #remove alignments in which both trees are parents of the trees of other alignments
        #NOT
        alignments=initialAlignments
        #for alignment in initialAlignments:
        for alignment in []:
            sltree=alignment[0][0]
            tltree=alignment[1][0]
            isParent=False
            for alignmentComparable in initialAlignments:
                if sltree in alignmentComparable[0][0].get_all_parents() and tltree in alignmentComparable[1][0].get_all_parents():
                    isParent=True
                    break
            if not isParent:
                alignments.append(alignment)
        
        #create alignment object
        alObjs=list()
        for alignment in alignments:
            try:
                al=Alignment(alignment[0][0],sourceSimpleExtendedExprs[alignment[0][1]],alignment[1][0],targetSimpleExtendedExprs[alignment[1][1]])
                alObjs.append(al)
            except ExprNotFoundException as ex:
                print >> sys.stderr, "WARNING: could not find expr for aligned bracketed "+ex.blame
        
        #remove conflicting alignments, only if bilphrases have not been used
        #if args.bilingual_phrases:
        if False:
            alsTLUnconflicted=alObjs
        else:
            #first left side
            alsSLUnconflicted=list()
            leftSideDict=dict()
            for al in alObjs:
                if not al.slexpr in leftSideDict:
                    leftSideDict[al.slexpr]=[]
                leftSideDict[al.slexpr].append(al)
            for slexpr in leftSideDict.keys():
                als=leftSideDict[slexpr]
                if len(als) ==1:
                    alsSLUnconflicted.append(als[0])
                else:
                    #First heuristic: choose alignment sharing function name
                    alsSharingFun=[al for al in als if al.tlexpr.fun == slexpr.fun]
                    resultFirstHeuristic=list()
                    if len(alsSharingFun) == 0:
                        print >> sys.stderr, "WARNING: no TL alignment sharing function found for SL expr '"+str(slexpr)+"'. Trying second heuristic"
                        resultFirstHeuristic.extend(als)
                    else:
                        if len(alsSharingFun) > 1:
                            print >> sys.stderr, "WARNING: More than one TL alignment sharing function found for SL expr '"+str(slexpr)+"'. Trying second heuristic"
                        resultFirstHeuristic.extend(alsSharingFun)
                    
                    #NO!! Second heuristic: align with the tree whose number of leaf functions is the most similar
                    #Second heuristic: align with the smallest tree
                    if len(resultFirstHeuristic) > 1:
                        if False:
                            alsWithDifferenceInNumLeafs=[( abs(len(al.tlexpr.leaf_functions)-len(slexpr.leaf_functions)) ,al) for al in resultFirstHeuristic]
                            alsWithDifferenceInNumLeafsSorted=sorted(alsWithDifferenceInNumLeafs,key=itemgetter(0))
                            
                            #choose trees with the same difference than the first one
                            chosenTrees=[ pair[1] for pair in alsWithDifferenceInNumLeafsSorted if pair[0]==alsWithDifferenceInNumLeafsSorted[0][0]]
                            if len(chosenTrees) > 1:
                                print >> sys.stderr, "WARNING: More than one TL alignment with the same minimum leaf function difference found for SL expr '"+slexpr.to_string()+"'. Including all of them"
                            alsSLUnconflicted.extend(chosenTrees)
                        #
                        alsSortedByDepth=sorted(resultFirstHeuristic,key=lambda al: al.tlexpr.compute_max_depth_recursively())
                        alsSLUnconflicted.append(alsSortedByDepth[0])
                        
                    else:
                        alsSLUnconflicted.extend(resultFirstHeuristic)
                    
            
            #then right side
            alsTLUnconflicted=list()
            rightSideDict=dict()
            for al in alsSLUnconflicted:
                if not al.tlexpr in rightSideDict:
                    rightSideDict[al.tlexpr]=[]
                rightSideDict[al.tlexpr].append(al)
            for tlexpr in rightSideDict.keys():
                als=rightSideDict[tlexpr]
                if len(als) ==1:
                    alsTLUnconflicted.append(als[0])
                else:
                    #First heuristic: choose alignment sharing function name
                    resultFirstHeuristic=list()
                    alsSharingFun=[al for al in als if al.slexpr.fun == tlexpr.fun]
                    if len(alsSharingFun) == 0:
                        print >> sys.stderr, "WARNING: no SL alignment sharing function found for TL expr '"+str(tlexpr)+"'. Trying second heuristic"
                        resultFirstHeuristic.extend(als)
                    else:
                        if len(alsSharingFun) > 1:
                            print >> sys.stderr, "WARNING: More than one SL alignment sharing function found for TL expr '"+str(tlexpr)+"'. Trying second heuristic"
                        resultFirstHeuristic.extend(alsSharingFun)
                    
                    #NO!! Second heuristic: align with the tree whose number of leaf functions is the most similar
                    #Second heuristic: align with the smallest tree
                    if len(resultFirstHeuristic) > 1:
                        if False:
                            alsWithDifferenceInNumLeafs=[( abs(len(al.slexpr.leaf_functions)-len(tlexpr.leaf_functions)) ,al) for al in resultFirstHeuristic]
                            alsWithDifferenceInNumLeafsSorted=sorted(alsWithDifferenceInNumLeafs,key=itemgetter(0))
                            
                            #choose trees with the same difference than the first one
                            chosenTrees=[ pair[1] for pair in alsWithDifferenceInNumLeafsSorted if pair[0]==alsWithDifferenceInNumLeafsSorted[0][0]]
                            if len(chosenTrees) > 1:
                                print >> sys.stderr, "WARNING: More than one SL alignment with the same minimum leaf function difference found for TL expr '"+str(tlexpr)+"'. Including all of them"
                            alsTLUnconflicted.extend(chosenTrees)
                        
                        alsSortedByDepth=sorted(resultFirstHeuristic,key=lambda al: al.slexpr.compute_max_depth_recursively())
                        alsTLUnconflicted.append(alsSortedByDepth[0])
                        
                    else:
                        alsTLUnconflicted.extend(resultFirstHeuristic)
        
        #print alignments
        for al in alsTLUnconflicted:
            print al.to_string(False)
            
            
            #print >> sys.stderr, "SL bracket: "+str(alignment[0][0])
            #print >> sys.stderr, "SL expr: "+str(slexpr)
            #print >> sys.stderr, "TL bracket: "+str(alignment[1][0])
            #print >> sys.stderr, "TL expr: "+str(tlexpr)
    if args.create_bilingual_dictionary:
        myfile=open(args.create_bilingual_dictionary,'w')
        bilingualDictionary.write(myfile)
        myfile.close()
        
        myfile=open(args.create_bilingual_dictionary+".inv",'w')
        bilingualDictionaryInv.write(myfile)
        myfile.close()
