#!/usr/bin/env python

from ruleLearningLib import uniprint
import sys,ruleLearningLib,unicodedata, string

def createGFToken(tokenname,category):
    return remove_accents(tokenname.replace(u"-","_").replace(u" ",u"_"))+u"_"+category
def createGFTokenNoValency(tokenname):
    return remove_accents(tokenname.replace(u"-","_").replace(u" ",u"_"))
def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters+"_").lower()

class LexicalFormNoCategories(ruleLearningLib.AT_LexicalForm):
    def compute_categories_of_tags(self):
        self.categories[:]=[]
        for tag in self.tags:
            self.categories.append(u"default")

class AbstractLineEntry(object):
    def __init__(self):
        raise NotImplementedError("Please Implement this method")
    
    def parse(self,rawstr):
        raise NotImplementedError("Please Implement this method")
    
    def get_representative(self):
        raise NotImplementedError("Please Implement this method")

class BilingualDicLineEntry(AbstractLineEntry):

    def __init__(self):
        self.leftSideLexicalForm=LexicalFormNoCategories()
        self.rightSideLexicalForm=LexicalFormNoCategories()

    def parse(self,rawstr):
        instr=rawstr.strip().decode('utf-8')
        parts=instr.split(u":")
        self.leftSideLexicalForm.parse(parts[0])
        self.rightSideLexicalForm.parse(parts[1])
    
    def get_representative(self):
        return self.leftSideLexicalForm.get_lemma()
        

class MonolingualDicLineEntry(AbstractLineEntry):
    def __init__(self):
        self.lexicalForm=LexicalFormNoCategories()
        self.surfaceForm=u""
    
    def parse(self,rawstr):
        instr=rawstr.strip().decode('utf-8')
        parts=instr.split(u":")
        self.surfaceForm=parts[1]
        self.lexicalForm.parse(parts[0])
    
    def get_representative(self):
        return self.lexicalForm.get_lemma()
    
    def __repr__(self):
        return self.surfaceForm.encode('utf-8')+":"+str(self.lexicalForm)

class ValencyEntry(AbstractLineEntry):
    def __init__(self):
        self.lemma=u""
        self.valency=u""
    
    def parse(self,rawstr):
        instr=rawstr.strip().decode('utf-8')
        parts=instr.split(u"_")
        self.valency=parts[-1]
        self.lemma=u"_".join(parts[:-1])
    
    def get_representative(self):
        return self.lemma
    
    def __repr__(self):
        return self.lemma.encode('utf-8')+":"+self.valency.encode('utf-8')

    

class AbstractGroupProcessor(object):
    
    printOnlyTokens=False
    blacklist=set()
    
    @staticmethod
    def can_print( token):
        return token not in AbstractGroupProcessor.blacklist
    
    @staticmethod
    def add_to_blacklist(token ):
        AbstractGroupProcessor.blacklist.add(token)

    @staticmethod
    def process(mygroup):
        raise NotImplementedError("Please Implement this method")

class MultipleLineEntriesProcessor(object):
    @staticmethod
    def read_group(mybuffer,entryClass,inputF):
        rawline=inputF.readline()
        lineEntry=None
        if len(rawline) > 0:
            lineEntry=entryClass()
            lineEntry.parse(rawline)
            while len(mybuffer)==0 or mybuffer[-1].get_representative() == lineEntry.get_representative():
                mybuffer.append(lineEntry)
                rawline=inputF.readline()
                if len(rawline) > 0:
                    lineEntry=entryClass()
                    lineEntry.parse(rawline)
                else:
                    break
        groupList=mybuffer[:]
        mybuffer[:]=[]
        if lineEntry:
            mybuffer.append(lineEntry)
        return groupList
    
    @staticmethod
    def process(groupProcessorClass,entryClass,inputF=sys.stdin):
        mybuffer=list()
        mygroup=MultipleLineEntriesProcessor.read_group(mybuffer,entryClass,inputF)
        while len(mygroup) > 0:
            groupProcessorClass.process(mygroup)
            mygroup=MultipleLineEntriesProcessor.read_group(mybuffer,entryClass,inputF)

