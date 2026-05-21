#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: quevedo@uniovi.es
"""

from sklearn.svm import LinearSVC
import numpy as np

class RobustLinearSVC(LinearSVC):
    """
    LinearSVC that:
    Can fit with:
        No samples                   : returns 0 in predict
        Samples of only one category : return this category in predict
        Samples of different lenght  : add zeros to right of each example to make 
          all sample have the same lenght
    Can predict:
        Samples of different lenght  : if add zeros to right or cut the sample
           to get samples of the same lenght that the ones in fit
    """
    def __init__(self,penalty='l2', loss='squared_hinge', *, dual='auto', 
                 tol=0.0001, C=1.0, multi_class='ovr', fit_intercept=True, 
                 intercept_scaling=1, class_weight=None, verbose=0, 
                 random_state=None, max_iter=1000):
        LinearSVC.__init__(self,penalty=penalty, loss=loss, dual=dual, 
                     tol=tol, C=C, multi_class=multi_class, fit_intercept=fit_intercept, 
                     intercept_scaling=intercept_scaling, class_weight=class_weight, verbose=verbose, 
                     random_state=random_state, max_iter=max_iter)
        # Model
        self.constantModel=None # For constant model (when all classes in train are the same)
        self.fitNAtt      =None # Number of attributes at fit

    def fit(self,X, y, sample_weight=None):
        if len(X)==0: # No samples
            self.constantModel=0 # If no samples return 0
            return self
        classes=np.unique(y)
        if len(classes)==1:
            self.constantModel=classes[0] # Constant model
        else:
            self.constantModel=None
            # Add right zeros to the samples until the max sample lenght
            maxl=max([len(row) for row in X])
            self.fitNAtt=maxl
            Xe=[]
            for x in X:
                xe=x+[0]*(maxl-len(x))
                Xe.append(xe)
            # Fit the model
            return LinearSVC.fit(self,Xe,y,sample_weight)
            
    
    def predict(self,X):
        if type(self.constantModel)!=type(None):
            return np.array([self.constantModel]*len(X)) # Constant prediction
        # Fix the number of attributes of X, adding 0 to right or getting the first fitNAtt attributes
        Xe=[]
        for x in X:
            if len(x)<self.fitNAtt:
                xe=np.concatenate([x,[0]*(self.fitNAtt-len(x))]) # Add right zeros
            else:
                xe=x[:self.fitNAtt]  # Cut by self.fitNAtt
            Xe.append(xe)
        return LinearSVC.predict(self,Xe)


                