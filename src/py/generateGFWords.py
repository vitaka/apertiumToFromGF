#!/usr/bin/env python

import argparse, sys
from lib.Utils import uniprint,unidecode
from lib.portApertiumToGFLib import createGFToken,createGFTokenNoValency,ApertiumLexformGroupProcessor,MultipleLineEntriesProcessor,MonolingualDicLineEntry,BilingualDicLineEntry,ValencyEntry


class EngAdjectivesProcessor(ApertiumLexformGroupProcessor):
    @classmethod
    def actual_process(cls,mygroup):
        if len(mygroup) > 1:
            #try to find comparative form and ensure that it contains
            # the <sint> tag
            compararativeForm=None
            baseForm=None
            for entry in mygroup:
                if u"comp" in entry.lexicalForm.get_tags() and u"sint" in entry.lexicalForm.get_tags():
                    compararativeForm=entry
                if u"comp" not in entry.lexicalForm.get_tags() and u"sup" not in entry.lexicalForm.get_tags():
                    baseForm=entry
            if compararativeForm and baseForm:
                EngAdjectivesProcessor.print_GF_synthetic(baseForm.lexicalForm.get_lemma(),baseForm.surfaceForm,compararativeForm.surfaceForm)
                return
            
        EngAdjectivesProcessor.print_GF_no_synthetic(mygroup[0].lexicalForm.get_lemma(),mygroup[0].lexicalForm.get_lemma())
        
    @staticmethod
    def print_GF_no_synthetic(lemma,baseform):
        token_id=createGFToken(lemma,u"A")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : A ;")
            else:
                uniprint(u"lin "+token_id+" = compoundA (mkA \""+baseform+"\") ;")
            #don't print an entry with the same token again
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)
    
    @staticmethod
    def print_GF_synthetic(lemma,baseform,comparativeForm):
        token_id=createGFToken(lemma,u"A")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : A ;")
            else:
                uniprint(u"lin "+token_id+" = mkA \""+baseform+"\" \""+comparativeForm+"\" ;")
            #don't print an entry with the same token again
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)

class EngNounsProcessor(ApertiumLexformGroupProcessor):
    @classmethod
    def actual_process(cls,mygroup):
        
        #discard feminine forms
        #if a noun has m and f form, we get only the m
        fgroup=list()
        for entry in mygroup:
            if not u"f" in entry.lexicalForm.get_tags():
                fgroup.append(entry)
        
        
        sgNoGenitiveForm=None
        plNoGenitiveForm=None
        sgGenitiveForm=None
        plGenitiveForm=None
        
        for entry in fgroup:
            if u"genitivesaxon" in entry.lexicalForm.get_tags():
                if u"sg" in entry.lexicalForm.get_tags():
                    sgGenitiveForm=entry.surfaceForm
                elif u"pl" in entry.lexicalForm.get_tags():
                    plGenitiveForm=entry.surfaceForm
            else:
                if u"sg" in entry.lexicalForm.get_tags():
                    sgNoGenitiveForm=entry.surfaceForm
                elif u"pl" in entry.lexicalForm.get_tags():
                    plNoGenitiveForm=entry.surfaceForm
        
        if sgNoGenitiveForm != None or plNoGenitiveForm != None:
            
            #copy missing singular or plural form
            #for nouns which have only a singular or only a plural form
            if plNoGenitiveForm == None:
                plNoGenitiveForm = sgNoGenitiveForm
            if sgNoGenitiveForm == None:
                sgNoGenitiveForm = plNoGenitiveForm
            
            if sgGenitiveForm != None or plGenitiveForm != None:
                #if no sh or pl genitive form is provided,
                #it means that it is regular
                if sgGenitiveForm == None:
                    sgGenitiveForm=sgNoGenitiveForm+u"'s"
                if plGenitiveForm == None:
                    plGenitiveForm = plNoGenitiveForm+u"'s"
                EngNounsProcessor.print_GF_genitive(fgroup[0].lexicalForm.get_lemma(),sgNoGenitiveForm,plNoGenitiveForm,sgGenitiveForm,plGenitiveForm)
            else:
                EngNounsProcessor.print_GF(fgroup[0].lexicalForm.get_lemma(),sgNoGenitiveForm,plNoGenitiveForm)
        else:
            print >> sys.stderr, "Discarded Group: "+str(mygroup)
    
    @staticmethod
    def print_GF( token, sgForm,plForm):
        token_id=createGFToken(token,u"N")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : N ;")
            else:
                uniprint(u"lin "+token_id+u" = mkN "+u" ".join([ u"\""+form+u"\"" for form in [sgForm,plForm] ])+u" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)
    
    @staticmethod
    def print_GF_genitive( token, sgForm,plForm, sgGenForm, plGenForm):
        token_id=createGFToken(token,u"N")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : N ;")
            else:
                uniprint(u"lin "+token_id+u" = mkN "+u" ".join([ u"\""+form+u"\"" for form in [sgForm,plForm, sgGenForm, plGenForm] ])+u" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)


class EngVblexProcessor(ApertiumLexformGroupProcessor):
    @classmethod
    def actual_process(cls,mygroup):
        tagsOfForms=[[u"inf"] , [u"pri",u"p3",u"sg"] , [u"past"] , [u"pp"] , [u"ger"] ]
        foundEntries=[ [] for mylist in tagsOfForms ]
        groupNoSep=[ entry for entry in mygroup if len ( set([u"hasprpers",u"hasthat",u"hasthis"]) & set(entry.lexicalForm.get_tags()) ) == 0 ]
        
        #search for tags in entries
        for i in range(len(tagsOfForms)):
            pattern=u".".join(tagsOfForms[i])
            for entry in groupNoSep:
                tagsOfLexicalForm=u".".join(entry.lexicalForm.get_tags())
                if tagsOfLexicalForm.count(pattern) > 0:
                    foundEntries[i].append(entry)
                    
        if all( len(pfoundEntries) > 0 for pfoundEntries in foundEntries ):
            valencies=ValenciesProcessor.valencyDict.get(createGFTokenNoValency(groupNoSep[0].lexicalForm.get_lemma()))
            if not valencies or len(valencies) == 0:
                EngVblexProcessor.print_GF(groupNoSep[0].lexicalForm.get_lemma(),[pfoundEntries[0].surfaceForm for pfoundEntries in foundEntries])
            else:
                for valency in valencies:
                    EngVblexProcessor.print_GF(groupNoSep[0].lexicalForm.get_lemma(),[pfoundEntries[0].surfaceForm for pfoundEntries in foundEntries],valency)
                
        else:
            print >> sys.stderr, "Discarded Group: "+str(mygroup)
    
    @staticmethod
    def print_GF(lemma, forms, valency=u"V"):
        if not valency in [u"V",u"V2",u"V3",u"VS",u"VV",u"VA",u"VQ"]:
            uniprint(u"unknown valency: "+valency,True)
            return
        token_id=createGFToken(lemma,valency)
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : "+valency+" ;")
            else:
                uniprint(u"lin "+token_id+u" =  "+ ( u"mk"+valency+u" (" if valency != u"V" else u""  ) +u" mkV "+u" ".join([ u"\""+form+u"\"" for form in forms ])+u" "+( u")" if valency != u"V" else u""  )+u"  ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)

class EngAdverbsProcessor(ApertiumLexformGroupProcessor):
    @classmethod
    def actual_process(cls,mygroup):
        if len(mygroup) > 0:
            EngAdverbsProcessor.print_GF(mygroup[0].lexicalForm.get_lemma(), mygroup[0].surfaceForm)
        
    @staticmethod
    def print_GF(lemma,surface):
        token_id=createGFToken(lemma,u"Adv")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : Adv ;")
            else:
                uniprint(u"lin "+token_id+u" = mkAdv \""+surface+u"\" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)

class EngProperNounsProcessor(ApertiumLexformGroupProcessor):
    @staticmethod
    def actual_process(mygroup):
        if len(mygroup) > 0:
            surfaceForm=mygroup[0].surfaceForm
            if len(mygroup) > 1:
                #if there is more than one form, get singular one
                singularEntries=[ entry for entry in mygroup if u"sg" in entry.lexicalForm.get_tags() ]
                if len(singularEntries) > 0:
                    surfaceForm=singularEntries[0].surfaceForm
                else:
                    print >> sys.stderr, "No singular form found in multiple group: "+str(mygroup)
            EngProperNounsProcessor.print_GF(mygroup[0].lexicalForm.get_lemma(), surfaceForm)
        
    @staticmethod
    def print_GF(lemma,surface):
        token_id=createGFToken(lemma,u"PN")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : PN ;")
            else:
                uniprint(u"lin "+token_id+u" = mkPN \""+surface+u"\" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)



class SpaAdjectivesProcessor(ApertiumLexformGroupProcessor):
    
    engAdjectivesDict=dict()
    
    @classmethod
    def actual_process(cls,mygroup):
        msForm=None
        mpForm=None
        fsForm=None
        fpForm=None
        for entry in mygroup:
            if (u"m" in entry.lexicalForm.get_tags() or u"mf" in entry.lexicalForm.get_tags()) and (u"sg" in entry.lexicalForm.get_tags() or u"sp" in entry.lexicalForm.get_tags()) and not u"sup" in entry.lexicalForm.get_tags():
                msForm=entry.surfaceForm
            if (u"m" in entry.lexicalForm.get_tags() or u"mf" in entry.lexicalForm.get_tags()) and (u"pl" in entry.lexicalForm.get_tags() or u"sp" in entry.lexicalForm.get_tags()) and not u"sup" in entry.lexicalForm.get_tags():
                mpForm=entry.surfaceForm
            if (u"f" in entry.lexicalForm.get_tags() or u"mf" in entry.lexicalForm.get_tags()) and (u"sg" in entry.lexicalForm.get_tags() or u"sp" in entry.lexicalForm.get_tags()) and not u"sup" in entry.lexicalForm.get_tags():
                fsForm=entry.surfaceForm
            if (u"f" in entry.lexicalForm.get_tags() or u"mf" in entry.lexicalForm.get_tags()) and (u"pl" in entry.lexicalForm.get_tags() or u"sp" in entry.lexicalForm.get_tags()) and not u"sup" in entry.lexicalForm.get_tags():
                fpForm=entry.surfaceForm
        
        if msForm and mpForm and fsForm and fpForm:
            if mygroup[0].lexicalForm.get_lemma() in SpaAdjectivesProcessor.engAdjectivesDict:
                for token in SpaAdjectivesProcessor.engAdjectivesDict[mygroup[0].lexicalForm.get_lemma()]:
                    SpaAdjectivesProcessor.print_GF(token,msForm,mpForm,fsForm,fpForm)
    
    @staticmethod
    def print_GF(token,ms,mp,fs,fp):
        token_id=createGFToken(token,u"A")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : A ;")
            else:
                uniprint(u"lin "+token_id+u" = mk4A "+u" ".join([ u"\""+form+u"\"" for form in [ms,fs,mp,fp] ])+u" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)

class SpaProperNounsProcessor(ApertiumLexformGroupProcessor):
    engDict=dict()
    
    @classmethod
    def actual_process(cls,mygroup):
        if len(mygroup) >0:
            #determine number: singular if there are singular and plural forms. The number of the form if all the forms have the same number
            numbers=set([ (set(entry.lexicalForm.get_tags()) & set([u"sg","pl"])).pop() for entry in mygroup ])
            number= u"sg" if len(numbers) > 1 else numbers.pop()
            entriesMatchingNumber=[ entry for entry in mygroup if number in entry.lexicalForm.get_tags() ]
            
            #determine gender: masculine if mf or different genders, The gender of the forms if all the forms have the same gender
            genders = set([ (set(entry.lexicalForm.get_tags()) & set([u"m","f","mf"])).pop() for entry in entriesMatchingNumber])
            genders = genders - set([u"mf"])
            gender = u"m" if len(genders) == 0 else genders.pop()
            entriesMatchingGender = [ entry for entry in entriesMatchingNumber if gender in entry.lexicalForm.get_tags() ]
            if len(entriesMatchingGender) > 0:
                surfaceForm=entriesMatchingGender[0].surfaceForm
            else:
                #probably mf
                surfaceForm=entriesMatchingNumber[0].surfaceForm
            
            if mygroup[0].lexicalForm.get_lemma() in SpaProperNounsProcessor.engDict:
                for token in SpaProperNounsProcessor.engDict[mygroup[0].lexicalForm.get_lemma()]:
                    SpaProperNounsProcessor.print_GF(token,gender,surfaceForm)
    
    @staticmethod
    def print_GF(token,gender,surfaceForm):
        genderDict= {u"m":u"masculine", u"f":u"feminine" }
        token_id=createGFToken(token,u"PN")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : PN ;")
            else:
                uniprint(u"lin "+token_id+u" = mkPN \""+surfaceForm+u"\" "+genderDict[gender]+u" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)
    


class SpaNounsProcessor(ApertiumLexformGroupProcessor):
    
    engNounsDict=dict()
    
    @classmethod
    def actual_process(cls,mygroup):
        sgPairs=list()
        plPairs=list()
        
        gendersSeen=set()
        finalGender=None
        for entry in mygroup:
            gendersSeen.add( [ tag for tag in entry.lexicalForm.get_tags() if tag in [u"m",u"f",u"mf"]][0] )
            if u"sg" in entry.lexicalForm.get_tags() or u"sp" in entry.lexicalForm.get_tags():
                sgPairs.append(entry)
            if u"pl" in entry.lexicalForm.get_tags() or u"sp" in entry.lexicalForm.get_tags():
                plPairs.append(entry)
        
        #we can have:
        # - both masculine and feminine forms
        # - mf form
        # - only m or only f forms
        if len(gendersSeen) > 1:
            finalGender=u"m"
            singularsWithGender = [ entry for entry in sgPairs if u"m" in entry.lexicalForm.get_tags() ]
            pluralsWithGender = [ entry for entry in plPairs if u"m" in entry.lexicalForm.get_tags() ]
        else:
            #only one gender seen
            #if mf, gender is m
            finalGender=gendersSeen.pop()
            if finalGender == u"mf":
                finalGender=u"m"
            
            singularsWithGender=sgPairs
            pluralsWithGender=plPairs
        
        #select sg and pl forms. If we have, for instance
        # sp and sg forms, choose sg form
        if len(singularsWithGender) > 1:
            sgForm=[ entry.surfaceForm for entry in singularsWithGender if u"sg" in entry.lexicalForm.get_tags() ][0]
        elif len(singularsWithGender) == 1:
            sgForm=singularsWithGender[0].surfaceForm
        else:
            sgForm=None
        
        if len(pluralsWithGender) > 1:
            plForm=[ entry.surfaceForm for entry in pluralsWithGender if u"pl" in entry.lexicalForm.get_tags() ][0]
        elif len(pluralsWithGender) == 1:
            plForm=pluralsWithGender[0].surfaceForm
        else:
            plForm=None
        
        if sgForm != None or plForm != None:
            if sgForm == None:
                sgForm=plForm
            if plForm == None:
                plForm=sgForm
            
            #obtain ENglish token from bilingual dictionary
            if mygroup[0].lexicalForm.get_lemma() in SpaNounsProcessor.engNounsDict:
                for token in SpaNounsProcessor.engNounsDict[mygroup[0].lexicalForm.get_lemma()]:
                    SpaNounsProcessor.print_GF(token,finalGender,sgForm,plForm)
            
        else:
            print >> sys.stderr, "Discarded Group: "+str(mygroup)
    
    @staticmethod
    def print_GF(token,gender,sgForm,plForm):
        genderDict= {u"m":u"masculine", u"f":u"feminine" }
        token_id=createGFToken(token,u"N")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : N ;")
            else:
                uniprint(u"lin "+token_id+u" = mkN "+u" ".join([ u"\""+form+u"\"" for form in [sgForm, plForm] ] + [genderDict[gender]])+u" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)

class SpaVblexProcessor(ApertiumLexformGroupProcessor):
    engVblexDict=dict()
    
    @classmethod
    def actual_process(cls,mygroup):
        tagsOfForms=[ u"inf" , u"ger" , u"pp.m.sg" , u"pri.p1.sg" , u"pri.p2.sg", u"pri.p3.sg" , u"pri.p1.pl" , u"pri.p2.pl", u"pri.p3.pl", u"prs.p1.sg" , u"prs.p2.sg", u"prs.p3.sg" , u"prs.p1.pl" , u"prs.p2.pl", u"prs.p3.pl", u"pii.p1.sg" , u"pii.p2.sg", u"pii.p3.sg" , u"pii.p1.pl" , u"pii.p2.pl", u"pii.p3.pl", u"pis.p1.sg" , u"pis.p2.sg", u"pis.p3.sg" , u"pis.p1.pl" , u"pis.p2.pl", u"pis.p3.pl", u"pis.p1.sg" , u"pis.p2.sg", u"pis.p3.sg" , u"pis.p1.pl" , u"pis.p2.pl", u"pis.p3.pl", u"ifi.p1.sg" , u"ifi.p2.sg", u"ifi.p3.sg" , u"ifi.p1.pl" , u"ifi.p2.pl", u"ifi.p3.pl", u"fti.p1.sg" , u"fti.p2.sg", u"fti.p3.sg" , u"fti.p1.pl" , u"fti.p2.pl", u"fti.p3.pl", u"pis.p1.sg" , u"pis.p2.sg", u"pis.p3.sg" , u"pis.p1.pl" , u"pis.p2.pl", u"pis.p3.pl", u"cni.p1.sg" , u"cni.p2.sg", u"cni.p3.sg" , u"cni.p1.pl" , u"cni.p2.pl", u"cni.p3.pl", u"imp.p1.pl" , u"imp.p2.sg", u"imp.p3.sg" , u"imp.p1.pl" , u"imp.p2.pl", u"imp.p3.pl", u"pp.m.sg", u"pp.f.sg", u"pp.m.pl", u"pp.f.pl"]
        foundEntries=[ [] for mylist in tagsOfForms ]
        
        #search for tags in entries
        for i in range(len(tagsOfForms)):
            pattern=tagsOfForms[i]
            for entry in mygroup:
                tagsOfLexicalForm=u".".join(entry.lexicalForm.get_tags())
                if tagsOfLexicalForm.count(pattern) > 0:
                    foundEntries[i].append(entry)
   
        if all( len(pfoundEntries) > 0 for pfoundEntries in foundEntries ):
            if not mygroup[0].lexicalForm.get_lemma() in SpaVblexProcessor.engVblexDict:
                print >> sys.stderr, "Discarded group: not found in bilingual: "+str(mygroup)
            else:
                for token in SpaVblexProcessor.engVblexDict[mygroup[0].lexicalForm.get_lemma()]:
                    valencies=ValenciesProcessor.valencyDict.get(createGFTokenNoValency(token))
                    if not valencies or len(valencies) == 0:
                        SpaVblexProcessor.print_GF(token,[pfoundEntries[0].surfaceForm for pfoundEntries in foundEntries])
                    else:
                        for valency in valencies:
                            SpaVblexProcessor.print_GF(token,[pfoundEntries[0].surfaceForm for pfoundEntries in foundEntries],valency)
        else:
            print >> sys.stderr, "Discarded Group: "+str(mygroup)
            
    @staticmethod
    def print_GF(token,forms,valency=u"V"):
        if not valency in [u"V",u"V2",u"V3",u"VS",u"VV",u"VA",u"VQ"]:
            uniprint(u"unknown valency: "+valency,True)
            return
        token_id=createGFToken(token,valency)
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : "+valency+" ;")
            else:
                addValencyStart=u""
                addValencyEnd=u""
                if valency != u"V":
                    addValencyEnd=u")"
                    if valency == u"V3":
                        addValencyStart= u"dirdirV3 ("
                    else:
                        addValencyStart= u"mk"+valency+u" ("
                uniprint(u"lin "+token_id+u" = "+addValencyStart+u" verboV  (allforms_67 "+u" ".join([ u"\""+form+u"\"" for form in forms ])+u" ) "+addValencyEnd+u" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)

class SpaAdverbsProcessor(ApertiumLexformGroupProcessor):
    
    engDict=dict()
    
    @classmethod
    def actual_process(cls,mygroup):
        if len(mygroup) > 0:
            if not mygroup[0].lexicalForm.get_lemma() in SpaAdverbsProcessor.engDict:
                print >> sys.stderr, "Discarded group: not found in bilingual: "+str(mygroup)
            else:
                for token in SpaAdverbsProcessor.engDict[mygroup[0].lexicalForm.get_lemma()]:
                    SpaAdverbsProcessor.print_GF(token, mygroup[0].surfaceForm)
        
    @staticmethod
    def print_GF(lemma,surface):
        token_id=createGFToken(lemma,u"Adv")
        if ApertiumLexformGroupProcessor.can_print(token_id):
            if ApertiumLexformGroupProcessor.printOnlyTokens:
                uniprint(token_id+u" : Adv ;")
            else:
                uniprint(u"lin "+token_id+u" = mkAdv \""+surface+u"\" ;")
            ApertiumLexformGroupProcessor.add_to_blacklist(token_id)

class SpaEngBilingualProcessor(ApertiumLexformGroupProcessor):
    
    bilingualDictionaryRepresentation=dict()
    
    @staticmethod
    def actual_process(mygroup):
        spaLemma=mygroup[0].leftSideLexicalForm.get_lemma()
        engLemmas=set()
        for entry in mygroup:
            engLemmas.add(entry.rightSideLexicalForm.get_lemma())
        SpaEngBilingualProcessor.bilingualDictionaryRepresentation[spaLemma]=list(engLemmas)

class ValenciesProcessor(object):
    #lemma -> [ valency1, valency2, ... ]
    valencyDict=dict()
    
    @classmethod
    def process(cls,mygroup):
        lemma=mygroup[0].lemma
        if not lemma in cls.valencyDict:
            cls.valencyDict[lemma]=[]
        for entry in mygroup:
            cls.valencyDict[entry.lemma].append(entry.valency)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates adjective for GF monolingual lexicon')
    parser.add_argument('--lang')
    parser.add_argument('--category')
    parser.add_argument('--bildic_tl_expanded_file')
    parser.add_argument('--print_only_tokens',action='store_true')
    parser.add_argument('--black_list')
    parser.add_argument('--valencies')
    parser.add_argument('--no_multiwords',action='store_true')

    args = parser.parse_args(sys.argv[1:])
    
    ApertiumLexformGroupProcessor.set_ignore_multiwords(args.no_multiwords)
    
    if args.print_only_tokens:
        ApertiumLexformGroupProcessor.printOnlyTokens=True
    
    if args.bildic_tl_expanded_file:
        #actual_process bilingual dictionary
        #we want as a result a dict() in python which contains, for each TL lemma
        #the different SL lemmas which is mapped from in the bilingual dictionary
        
        fileDesc=open(args.bildic_tl_expanded_file,'r')
        MultipleLineEntriesProcessor.process(SpaEngBilingualProcessor,BilingualDicLineEntry,fileDesc)
        if args.category == "adj":    
            SpaAdjectivesProcessor.engAdjectivesDict=SpaEngBilingualProcessor.bilingualDictionaryRepresentation
        elif args.category == "n":
            SpaNounsProcessor.engNounsDict=SpaEngBilingualProcessor.bilingualDictionaryRepresentation
        elif args.category == "np":
            SpaProperNounsProcessor.engDict=SpaEngBilingualProcessor.bilingualDictionaryRepresentation
        elif args.category == "vblex":
            SpaVblexProcessor.engVblexDict=SpaEngBilingualProcessor.bilingualDictionaryRepresentation
        elif args.category == "adv":
            SpaAdverbsProcessor.engDict=SpaEngBilingualProcessor.bilingualDictionaryRepresentation
        else:
            print >> sys.stderr, "Category not defined"
        fileDesc.close()
    
    if args.valencies:
        MultipleLineEntriesProcessor.process(ValenciesProcessor,ValencyEntry,open(args.valencies))
        #debug
        #print  "valencies for understand: "+str(ValenciesProcessor.valencyDict[u"understand"])
    
    if args.black_list:
        blacklist = set([unidecode(line).strip() for line in open(args.black_list)])
        ApertiumLexformGroupProcessor.blacklist=blacklist
        
    if args.lang == "en":
        if args.category == "adj":
            MultipleLineEntriesProcessor.process(EngAdjectivesProcessor,MonolingualDicLineEntry)
        elif args.category == "n":
            MultipleLineEntriesProcessor.process(EngNounsProcessor,MonolingualDicLineEntry)
        elif args.category == "vblex":
            MultipleLineEntriesProcessor.process(EngVblexProcessor,MonolingualDicLineEntry)
        elif args.category == "adv":
            MultipleLineEntriesProcessor.process(EngAdverbsProcessor,MonolingualDicLineEntry)
        elif args.category== "np":
            MultipleLineEntriesProcessor.process(EngProperNounsProcessor,MonolingualDicLineEntry)
        else:
            print >> sys.stderr, "Category not defined"
    elif args.lang == "es":
        if args.category == "adj":
            MultipleLineEntriesProcessor.process(SpaAdjectivesProcessor,MonolingualDicLineEntry)
        elif args.category == "n":
            MultipleLineEntriesProcessor.process(SpaNounsProcessor,MonolingualDicLineEntry)
        elif  args.category == "vblex":
            MultipleLineEntriesProcessor.process(SpaVblexProcessor,MonolingualDicLineEntry)
        elif args.category == "adv":
            MultipleLineEntriesProcessor.process(SpaAdverbsProcessor,MonolingualDicLineEntry)
        elif args.category== "np":
            MultipleLineEntriesProcessor.process(SpaProperNounsProcessor,MonolingualDicLineEntry)
        else:
            print >> sys.stderr, "Category not defined"
    else:
        print >> sys.stderr, "Language not defined"

