#!/usr/bin/env python 
#!-*- coding: utf-8 -*-

import numpy as np
from scipy import sparse as sp

__author__ = "Irshad Ahmad Bhat"
__version__ = "1.0"
__email__ = "irshad.bhat@research.iiit.ac.in"

class OneHotEncoder():
    """Transforms categorical features to continuous numeric features"""

    def __init__(self,sparse=True):
        self.sparse = sparse

    def fit(self, X):
        """Returns a list of dictionaries with each dictionary containing 
        key-index pairs for unique values of each feature. Keys represent 
        new features of the data and indexes represent positions of these 
        new features in transformed form of data."""

        data = np.asarray(X)
        unique_feats = []
        offset = 0
        for i in range(data.shape[1]):
            feat_set_i = set(data[:,i])
            d = {val:i+offset for i,val in enumerate(feat_set_i)}
            unique_feats.append(d)
            offset += len(feat_set_i)
    
        self.unique_feats = unique_feats
        return self
    
    def transform(self, X):
        """One-hot representation (feature-hashing) is a fast and space-efficient 
        way of converting categorical features to numeric features, by turning 
        these features into indices in a vector or matrix. Here the feature and its
        index position is obtained using fit method."""
        if self.sparse:
            one_hot_matrix = sp.lil_matrix((len(X), sum(len(i) for i in self.unique_feats)))
        else:
            one_hot_matrix = np.zeros((len(X), sum(len(i) for i in self.unique_feats)), bool)
        for i,vec in enumerate(X):
            for j,val in enumerate(vec):
                if val in self.unique_feats[j]:
                    one_hot_matrix[i, self.unique_feats[j][val]] = 1.0
    
        return sp.csr_matrix(one_hot_matrix) if self.sparse else one_hot_matrix
