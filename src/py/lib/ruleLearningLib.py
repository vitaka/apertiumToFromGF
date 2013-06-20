# coding=utf-8
# -*- encoding: utf-8 -*-
import re
import sys
import traceback



class AT_FeatureNameValuePair(object):
	def __init__(self,featureName,value):
		self.feature_name=featureName
		self.feature_value=value
	

class AT_AbstractClassPosAndTags(object):
	def __init__(self):
		self.pos=u""
		self.tags=list()
		self.categories=list()
		
	def parse(self, mystr):
		parsed_tags=parse_tags(mystr)
		self.pos=parsed_tags[0]
		self.tags=parsed_tags[1:]
		self.compute_categories_of_tags()
	
	def compute_categories_of_tags(self):
		if AT_LexicalTagsProcessor.taggroups:
			self.categories[:]=[]
			for tag in self.tags:
				self.categories.append(get_tag_group_from_tag(tag,AT_LexicalTagsProcessor.taggroups,self.pos))
		#else:
		#	print >> sys.stderr, "WARNING: No tag groups defined. Cannot obtain feature names of tags"
	
	def unparse(self):
		raise NotImplementedError("Please Implement this method")
	
	def get_tags_with_feature_names(self):
		outputlist=list()
		for i in range(len(self.tags)):
			pair=AT_FeatureNameValuePair(self.categories[i],self.tags[i])
			outputlist.append(pair)
		return outputlist
	def get_tags_with_feature_names_as_dict(self):
		outputdict=dict()
		for i in range(len(self.tags)):
			outputdict[self.categories[i]]=self.tags[i]
		return outputdict
	
	def get_lexical_category_plus_tags(self):
		outputlist=list()
		outputlist.append(self.pos)
		outputlist.extend(self.tags)
		return outputlist	

	def set_tag_value_for_name(self,featureName, featureValue ):		
		position=self.categories.index(featureName)
		self.tags[position]=featureValue
	
	def get_categories(self):
		return self.categories	

	def get_tags(self):
		return self.tags
	
	def set_tags(self,p_tags):
		self.tags=p_tags
		self.compute_categories_of_tags()
	
	def get_pos(self):
		return self.pos
	def set_pos(self, p_pos):
		self.pos=p_pos
	
	def __eq__(self, other):
		if self.pos != other.pos:
			return False
		if self.tags != other.tags:
			return False
		return True

class AT_LexicalForm(AT_AbstractClassPosAndTags):
	def __init__(self):
		AT_AbstractClassPosAndTags.__init__(self)
		self.lemma=u""
	
	def set_values(self,p_lemma,p_pos,p_tags):
		self.set_lemma(p_lemma)
		self.set_pos(p_pos)
		self.set_tags(p_tags)
	
	
	def parse(self,lexformstr,removeUnderscoreFromLemma=False):
		if removeUnderscoreFromLemma:
			self.lemma=get_lemma(lexformstr).replace(u"_",u" ")
		else:
			self.lemma=get_lemma(lexformstr).replace(u"_",u" ")
		AT_AbstractClassPosAndTags.parse(self,lexformstr)
		
	def unparse(self,replaceSpacesWithUnderscore=False):
		if replaceSpacesWithUnderscore:
			return self.lemma.replace(u" ",u"_")+unparse_tags([self.pos]+self.tags)
		else:
			return self.lemma+unparse_tags([self.pos]+self.tags)

	
	def has_lemma(self):
		return len(self.lemma) > 0
	
	def get_lemma(self):
		return self.lemma
	
	
	def remove_lemma(self):
		self.set_lemma(u"")
	
	def set_lemma(self, lemmaval):
		self.lemma=lemmaval
	
	
	def __eq__(self, other):
		if not isinstance(other, AT_LexicalForm):
			return False
		if self.lemma != other.lemma:
			return False
		if not AT_AbstractClassPosAndTags.__eq__(self,other):
			return False
		return True
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __repr__(self):
		return (self.lemma+u"-"+u".".join([self.pos]+self.tags)).encode('utf-8')
	

class AT_LexicalTagsProcessor(object):
	taggroups = None
	tagsequences = None
	
	@staticmethod
	def initialize(taggroups_f,tagsequences_f):
		if taggroups_f:
			tag_groups_file=open(taggroups_f,'r')
			AT_LexicalTagsProcessor.taggroups=read_tag_groups(tag_groups_file)
			tag_groups_file.close()

		if tagsequences_f:
			tagsequencesfile=open(tagsequences_f)
			AT_LexicalTagsProcessor.tagsequences=read_tag_sequences(tagsequencesfile)
			tagsequencesfile.close()
	
	@staticmethod
	def add_explicit_empty_tags(pos,parsed_tags,weAreProcessingRestrictions=False):
		oldtagslist=parsed_tags[:]
		
		if pos in AT_LexicalTagsProcessor.tagsequences:
			newtagslist=list()
			groupsequence=AT_LexicalTagsProcessor.tagsequences[pos]
			for groupid in groupsequence:
				tag=find_tag_from_tag_group_in_tag_sequence(oldtagslist,groupid,AT_LexicalTagsProcessor.taggroups,pos)
				if tag!=None:
					newtagslist.append(tag)
				else:
					newtagslist.append(u"empty_tag_"+groupid)
					
			if weAreProcessingRestrictions:
				lastindexofnotemptytag=-1
				for i in range(len(newtagslist)):
					if not newtagslist[i].startswith(u"empty_tag_"):
						lastindexofnotemptytag=i	
				newtagslist=newtagslist[:lastindexofnotemptytag+1]
			return newtagslist
		else:
			return oldtagslist
	@staticmethod
	def get_tag_group_names():
		return AT_LexicalTagsProcessor.taggroups.keys()

def read_tag_groups(inputfile):
	tag_groups=dict()
	for line in inputfile:
		line=line.strip().decode('utf-8')
		parts=line.split(u":")
		if len(parts)==2 or len(parts)==3:
			groupname=parts[0]
			tags=parts[1].split(u",")
			pos=None
			if len(parts)==3:
				pos=parts[2]
			tag_groups[groupname]=(tags,pos)
	return tag_groups
	
def read_tag_sequences(inputfile):
	tag_sequences=dict()
	for line in inputfile:
		line=line.strip().decode('utf-8')
		parts=line.split(u":")
		if len(parts)==2:
			pos=parts[0]
			tags=parts[1].split(u",")
			tag_sequences[pos]=tags
	return tag_sequences


def find_tag_from_tag_group_in_tag_sequence(sequence,taggroup_id,taggroups,pos,usingEmptyTags=False):
	for tag in sequence:
		taggroup=get_tag_group_from_tag(tag,taggroups,pos,usingEmptyTags)
		if taggroup == taggroup_id:
			return tag
	return None

def get_tag_group_from_tag(tag,taggroups,pos,usingEmptyTags=True):
	DEBUG=False
	
	#debug("Getting group of '"+tag+"', which is a '"+pos+"'. Using empty tags = "+str(usingEmptyTags))
	
	EMPTY_TAG_PREFIX=u"empty_tag_"
	groupFound=None
	
	typeSpecial,featureName,postion= parse_special_tag(tag)
	
	if tag==pos:
		groupFound=u"__GROUP_PART_OF_SPEECH__"
	elif typeSpecial == AT_SpecialTagType.FOLLOW_ALIGNMENT or typeSpecial == AT_SpecialTagType.CHECK_BIDIX or typeSpecial == AT_SpecialTagType.SPECIFIED_SL:
		groupFound=featureName
	else:
		if tag.startswith(EMPTY_TAG_PREFIX) and usingEmptyTags:
			return tag[len(EMPTY_TAG_PREFIX):]
		else:
			numGroupsFound=0
			for groupIndex in taggroups.keys():
				if tag in taggroups[groupIndex][0] and (pos==taggroups[groupIndex][1] or None==taggroups[groupIndex][1]):
					numGroupsFound+=1
					groupFound=groupIndex
			if numGroupsFound!=1:
				print >> sys.stderr, "ERROR: tag '"+str(tag)+"' found in "+str(numGroupsFound)+" groups != 1"
				traceback.print_stack()
				exit()
	
	return groupFound

class AT_SpecialTagType:
	FOLLOW_ALIGNMENT=1
	SPECIFIED_SL=4
	CHECK_BIDIX=2
	NO_SPECIAL=3

def parse_special_tag(tag):
	if tag.startswith(u"*"):
		return AT_SpecialTagType.FOLLOW_ALIGNMENT,tag[1:],None
	elif tag.startswith(u")"):
		return AT_SpecialTagType.CHECK_BIDIX,tag[4:],int(tag[1:4])
	elif tag.startswith(u"("):
		return AT_SpecialTagType.SPECIFIED_SL,tag[4:],int(tag[1:4])
	else:
		return AT_SpecialTagType.NO_SPECIAL,None,None

def parse_tags(tagsstr):
	parsedTags=list()
	REGULAR_EXP=r"<([^>]+)>"
	pattern=re.compile(REGULAR_EXP)
	matchesiter=pattern.finditer(tagsstr)
	for mymatch in matchesiter:
		parsedTags.append(mymatch.group(1))
	return parsedTags

def unparse_tags(tagsstr):
	return u"<"+u"><".join(tagsstr)+u">"

def get_lemma(word):
	posStartTags=word.find(u"<")
	return word[:posStartTags]
