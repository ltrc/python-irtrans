#!/usr/bin/env python 
#!-*- coding: utf-8 -*-

"""
Transliteration Tool:
Roman to Indic transliterator
"""

import re
import os
import sys
import codecs
import warnings

import numpy as np

import viterbi
import one_hot_repr
from converter_indic import wxConvert

warnings.filterwarnings("ignore")

__author__ = "Irshad Ahmad Bhat"
__version__ = "1.0"
__email__ = "irshad.bhat@research.iiit.ac.in"

class RI_Transliterator():
    """Transliterates words from Roman to Indic script"""

    def __init__(self, lang): 
        self.lookup = dict()
	self.n , self.tab, self.space = 4, '~~', '^^'
        self.con = wxConvert(order='wx2utf', lang=lang)
	lang = lang[0]
        path = os.path.abspath(__file__).rpartition('/')[0]
        sys.path.append(path)
        self.vec = np.load('%s/models/e%s_vec.npy' %(path, lang))[0]
	self.coef_ = np.load('%s/models/e%s_coef.npy' %(path, lang))[0]
	self.classes_ = np.load('%s/models/e%s_classes.npy' %(path, lang))[0]
        self.intercept_init_ = np.load('%s/models/e%s_intercept_init.npy' %(path, lang))
        self.intercept_trans_ = np.load('%s/models/e%s_intercept_trans.npy' %(path, lang))
        self.intercept_final_ = np.load('%s/models/e%s_intercept_final.npy' %(path, lang))

    def feature_extraction(self, letters):
        out_letters = list()
        dummies = ["_"] * self.n
        context = dummies + letters + dummies
        for i in range(self.n, len(context)-self.n):
            current_token = context[i]
            wordContext = context[i-self.n:i] + [current_token] + context[i+1:i+(self.n+1)]
            word_ngram_context = wordContext + ["%s|%s" % (p,q) for p,q in zip(wordContext[:-1], wordContext[1:])] + \
                ["%s|%s|%s" % (r,s,t) for r,s,t in zip(wordContext[:-2], wordContext[1:], wordContext[2:])] +\
                ["%s|%s|%s|%s" % (u,v,w,x) for u,v,w,x in zip(wordContext[:-3],wordContext[1:],wordContext[2:],wordContext[3:])]
            out_letters.append(word_ngram_context)

        return out_letters

    def predict(self, word):   
        X = self.vec.transform(word)
        scores = X.dot(self.coef_.T).toarray() 

        y = viterbi.decode(scores, self.intercept_trans_,
               self.intercept_init_, self.intercept_final_)
        y =  [self.classes_[pred] for pred in y]

        return re.sub('_','',''.join(y))

    def case_trans(self, word):
        if not word:
            return u''
        if not word.isalpha():
            return word
        if word in self.lookup:
            return self.con.convert(self.lookup[word])
	word = word.encode('utf-8')
        word_feats = self.feature_extraction(list(word))
        op_word = self.predict(word_feats)
        self.lookup[word] = op_word

        return self.con.convert(op_word)

    def transliterate(self, text):
        tline = str()
	if not isinstance(text, unicode):
	    text = text.decode('utf-8')
        lines = text.split("\n")
	for line in lines:
	    if not line.strip():
                tline += "\n"
		continue
	    line = line.lower()
            line = line.replace('\t', self.tab)
            line = line.replace(' ', self.space)
            line = re.sub(r'([a-z])\.([a-z])', r'\1\2', line)
            line = ' '.join(re.split(r"([^a-z]+)", line)).split()
            for word in line:
		if word == self.space:
		    tline += " "
		elif word == self.tab:
		    tline += "\t"
		elif not word.isalpha():
		    tline += word.encode('utf-8')
		else:
		    op_word = self.case_trans(word)
		    tline += op_word
	    tline += "\n"

	tline = tline.replace(self.space, ' ')
        tline = tline.replace(self.tab, '\t')

        return tline.strip()
