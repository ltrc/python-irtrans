#!/usr/bin/env python 
# -*- coding: utf-8 -*-

#Copyright (C) 2015 Irshad Ahmad Bhat

"""
Transliteration Tool:
Roman to Indic transliterator
"""

import re
import sys
import string
import os.path
import warnings

import numpy as np

from ._decode import viterbi
from converter_indic import wxConvert

warnings.filterwarnings("ignore")

class RI_Transliterator():
    """Transliterates words from Roman to Indic script"""

    def __init__(self, lang): 
        self.lookup = dict()
        self.tab = '\x01\x04'
        self.space = '\x02\x03'

        self.fit(lang)

    def fit(self, lang):
	self.non_alpha = re.compile(r"([^a-z]+)")
	self.letters = set(string.ascii_letters[:26])
        dist_dir = os.path.dirname(os.path.abspath(__file__))
        self.con = wxConvert(order='wx2utf', lang=lang, rmask=False)

        #load models
	lg = lang[0]
        sys.path.append('%s/_utils' %dist_dir)
        self.vectorizer_      = np.load('%s/models/e%s_vec.npy' %(dist_dir, lg))[0]
	self.coef_	      = np.load('%s/models/e%s_coef.npy' %(dist_dir, lg))[0]
	self.classes_	      = np.load('%s/models/e%s_classes.npy' %(dist_dir, lg))[0]
        self.intercept_init_  = np.load('%s/models/e%s_intercept_init.npy' %(dist_dir, lg))
        self.intercept_trans_ = np.load('%s/models/e%s_intercept_trans.npy' %(dist_dir, lg))
        self.intercept_final_ = np.load('%s/models/e%s_intercept_final.npy' %(dist_dir, lg))

    def feature_extraction(self, letters):
        ngram = 4
        out_letters = list()
        dummies = ["_"] * ngram
        context = dummies + letters + dummies
        for i in range(ngram, len(context)-ngram):
            unigrams  = context[i-ngram: i] + [context[i]] + context[i+1: i+(ngram+1)]
            bigrams   = ["%s|%s" % (p,q) for p,q in zip(unigrams[:-1], unigrams[1:])]
            trigrams  = ["%s|%s|%s" % (r,s,t) for r,s,t in zip(unigrams[:-2], unigrams[1:], unigrams[2:])]
            quadgrams = ["%s|%s|%s|%s" % (u,v,w,x) for u,v,w,x in zip(unigrams[:-3], unigrams[1:], unigrams[2:], unigrams[3:])]
            ngram_context = unigrams + bigrams + trigrams + quadgrams
            out_letters.append(ngram_context)

        return out_letters

    def predict(self, word):
        X = self.vectorizer_.transform(word)
        scores = X.dot(self.coef_.T).toarray()
        y = viterbi.decode(scores, self.intercept_trans_,
                self.intercept_init_, self.intercept_final_)

        y =  [self.classes_[pid] for pid in y]
        y = ''.join(y)

        return y.replace('_', '')

    def case_trans(self, word):
        if word in self.lookup:
            return self.con.convert(self.lookup[word])
	word = word.encode('utf-8')
        word_feats = self.feature_extraction(list(word))
        op_word = self.predict(word_feats)
        self.lookup[word] = op_word

        return self.con.convert(op_word)

    def transliterate(self, text):
        trans_list = list()
        if isinstance(text, str):
            text = text.decode('utf-8')
        #text = re.sub(r'([a-z])\.([a-z])', r'\1\2', line)
	text = text.lower()
        text = text.replace('\t', self.tab)
        text = text.replace(' ', self.space)
        lines = text.split("\n")
	for line in lines:
	    if not line.strip():
                trans_list.append(line.encode('utf-8'))
                continue
	    trans_line = str()
	    line = self.non_alpha.split(line)
            for word in line:
                if not word:
                    continue
                elif word[0] not in self.letters:
                    trans_line += word.encode('utf-8')
                else:
                    op_word = self.case_trans(word)
                    trans_line += op_word
            trans_list.append(trans_line)

        trans_line = '\n'.join(trans_list)
        trans_line = trans_line.replace(self.space, ' ')
        trans_line = trans_line.replace(self.tab, '\t')

        return trans_line
