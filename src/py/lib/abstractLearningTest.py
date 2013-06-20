'''
Created on 21/05/2013

@author: vitaka
'''
import unittest,pgf
from abstractLearningLib import ExtendedExpr
from lib.abstractLearningLib import BilingualExpr, ParallelMWE,\
    BilingualPhraseSet

class ExtendedExprTest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.myexpr=pgf.readExpr("AdjCN (PositA crucial_A) (UseN item_N)")
        self.myexprw=pgf.readExpr("AdjCN (PositA crucial_A) (UseN wildcard_1)")
        self.myexprq=pgf.readExpr("CompoundCN ? wildcard_3 (AdjCN (PositA wildcard_1) (UseN wildcard_2))")
        self.myexprs=pgf.readExpr('(PredVP (DetCN (DetQuant IndefArt NumSg) (PossNP (AdjCN (PositA complete_A) (UseN collapse_N)) (UseQuantPN DefArt (SymbPN (MkSymb "U"))))) (UseComp (CompNP (MassNP (UseN dollar_N)))))')
        self.extExpr=ExtendedExpr(self.myexpr,None)
        self.extExprW=ExtendedExpr(self.myexprw,None)
        self.extExprQ=ExtendedExpr(self.myexprq,None)
        self.extExprS=ExtendedExpr(self.myexprs,None)
        self.bilingualPhraseSet=BilingualPhraseSet()
        self.bilingualPhraseSet.add("NATO ||| la OTAN ||| 0-0 0-1")
        
        self.mwe1=ParallelMWE()
        self.mwe1.parse("( MassNP ( UseN safety_N ) ) | ( DetCN ( DetQuant wildcard_IGNORE wildcard_IGNORE ) ( UseN security_N ) )")
        
        self.mwe2=ParallelMWE()
        self.mwe2.parse("( PossNP ( UseN wildcard_1 ) ( MassNP ( AdjCN ( PositA wildcard_2 ) ( UseN politics_N ) ) ) ) | ( PossNP ( UseN wildcard_1 ) ( DetCN ( DetQuant wildcard_IGNORE wildcard_IGNORE ) ( AdjCN ( PositA wildcard_2 ) ( UseN policy_N ) ) ) )")
        
        self.bilphrase=BilingualExpr()
        self.bilphrase.parse("( MassNP ( AdjCN ( PositA wildcard_2 ) ( UseN politics_N ) ) )  | ( DetCN ( DetQuant wildcard_IGNORE wildcard_IGNORE ) ( AdjCN ( PositA wildcard_2 ) ( UseN policy_N ) ) )", ignoreFreq=True)
        
        synDict=dict()
        synDict["politics_N"]=set(["policy_N"])
        ParallelMWE.synonymDict=synDict
    
    def testNonLeafFunList(self):
        listOfFuns=self.extExpr.get_non_leaf_funtions()
        assert listOfFuns == ['AdjCN', 'PositA', 'UseN']
        
    def testLeafFunList(self):
        listOfFuns=self.extExpr.get_leaf_functions()
        assert listOfFuns == ['crucial_A','item_N']
        
        listOfFuns=self.extExprS.get_leaf_functions()
        self.assertEqual(listOfFuns , ['IndefArt','NumSg','complete_A','collapse_N','DefArt','String_U','dollar_N'])
        
        listOfFuns=self.extExprQ.get_leaf_functions()
        self.assertEqual(listOfFuns, ['?','wildcard_3','wildcard_1','wildcard_2']) 
    
    def testWildcardFunList(self):
        listOfFuns=self.extExprW.get_wildcard_leaf_functions()
        self.assertEqual(listOfFuns,['wildcard_1'])
    
    def testExtractCandidateMWEs(self):
        bilExpr=BilingualExpr()
        bilExpr.set_exprs(self.extExpr,self.extExpr)
        self.assertTrue(bilExpr.is_equal_sides())
        
        candidateMWEs=bilExpr.extract_candidate_mwes()
        self.assertEqual(len(candidateMWEs), 4)
        for mwestr in candidateMWEs:
            mwe =ParallelMWE()
            mwe.parse(" | ".join(mwestr.split(" | ")[2:]))
            self.assertTrue(mwe.is_equal_sides())
    
    def testPrint(self):
        strrep=str(self.extExpr)
        myexpragain=pgf.readExpr(strrep)
        self.assertEqual(str(self.myexpr), str(myexpragain))
        
        strrep=str(self.extExprS)
        myexpragain=pgf.readExpr(strrep)
        self.assertEqual(str(self.myexprs), str(myexpragain))
    
    def testBilingualPhraseSet(self):
        self.assertTrue(self.bilingualPhraseSet.contains_biligual_phrase("NATO", "OTAN"))
        self.assertTrue(self.bilingualPhraseSet.contains_biligual_phrase("NATO", "la OTAN"))
        self.assertTrue(self.bilingualPhraseSet.contains_biligual_phrase("NATO", "la"))
    
    def testCompositionally(self):
        self.assertFalse(self.mwe1.is_bilexpr_matched_or_reproduced(self.bilphrase).reproduced)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
