#!/usr/bin/env python 
#!-*- coding: utf-8 -*-

"""
Transliteration Tool:
Indic to Roman transliterator
"""

import os
import re
import sys
import codecs
import warnings

import numpy as np
from scipy.sparse import csc_matrix

import viterbi
import one_hot_repr
from converter_indic import wxConvert

warnings.filterwarnings("ignore")

__author__ = "Irshad Ahmad"
__version__ = "1.0"
__email__ = "irshad.bhat@research.iiit.ac.in"

class IR_Transliterator():
    """Transliterates words from Indic to Roman script"""

    def __init__(self, lang):        

        self.lookup = dict()
	self.esc_char = chr(0)
        self.n = 4
        self.tab = '`%s`' %(chr(1))
        self.space = '`%s`' %(chr(2))
        self.con = wxConvert(order='utf2wx', lang=lang)
	lang = lang[0]
        path = os.path.abspath(__file__).rpartition('/')[0]
        sys.path.append(path)
        self.vec = np.load('%s/models/%se_vec.npy' %(path, lang))[0]
	self.coef_ = np.load('%s/models/%se_coef.npy' %(path, lang))[0]
	self.classes_ = np.load('%s/models/%se_classes.npy' %(path, lang))[0]
	self.intercept_init_ = np.load('%s/models/%se_intercept_init.npy' %(path, lang))
	self.intercept_trans_ = np.load('%s/models/%se_intercept_trans.npy' %(path, lang))
	self.intercept_final_ = np.load('%s/models/%se_intercept_final.npy' %(path, lang))

    def feature_extraction(self, letters):
        out_word = list()
        dummies = ["_"] * self.n
        context = dummies + letters + dummies
        for i in range(self.n, len(context)-self.n):
            current_token = context[i]
            wordContext = context[i-self.n:i] + [current_token] + context[i+1:i+(self.n+1)]
            word_ngram_context = wordContext + ["%s|%s" % (p,q) for p,q in zip(wordContext[:-1], wordContext[1:])] +\
                ["%s|%s|%s" % (r,s,t) for r,s,t in zip(wordContext[:-2], wordContext[1:], wordContext[2:])] +\
                ["%s|%s|%s|%s" % (u,v,w,x) for u,v,w,x in zip(wordContext[:-3],wordContext[1:],wordContext[2:],wordContext[3:])] 
            out_word.append(word_ngram_context)

        return out_word

    def predict(self, word):
        X = self.vec.transform(word)
        scores = X.dot(self.coef_.T).toarray()

        y = viterbi.decode(scores, self.intercept_trans_, self.intercept_init_, self.intercept_final_)
        y = [self.classes_[pred] for pred in y]
	y = ''.join(y)
	y = y.replace('_', '')

        return y

    def case_trans(self, word):
        if not word:
            return u''
        if not word.isalpha():
            return word
        if word in self.lookup:
            return self.lookup[word]
        word_feats = ' '.join(word).replace(' a', 'a').replace(' Z', 'Z')
        word_feats = word_feats.encode('utf-8').split()
        word_feats = self.feature_extraction(word_feats)
        op_word = self.predict(word_feats).decode('utf-8')
        self.lookup[word] = op_word

        return op_word

    def transliterate(self, text):
        tline = str()
	text = re.sub(r'([a-zA-Z]+)', r'%s\1' %(self.esc_char), text)
	lines = text.split("\n")
	for line in lines:
	    if not line.strip():
                tline += "\n"
            line = self.con.convert(line).decode('utf-8')  # Convert to wx
            line = line.replace('\t', self.tab)
            line = line.replace(' ', self.space)
            line = ' '.join(re.split(r"([^a-zA-Z%s]+)" %(self.esc_char), line)).split()
            for word in line:
		if word[0] == self.esc_char:
		    tline += word[1:].encode('utf-8')
                elif not word[0].isalpha():
                    tline += word.encode('utf-8')
		else:
		    op_word = self.case_trans(word)
		    tline += op_word.encode('utf-8')
	    tline += "\n"
	
	tline = tline.replace(self.space, ' ')
	tline = tline.replace(self.tab, '\t')
      
        return tline.strip('\n')
