#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: quevedo@uniovi.es
"""

from Chat import Chat
from sklearn.feature_extraction.text import CountVectorizer
from RobustLinearSVC import RobustLinearSVC

class BoWChat(Chat):
    """
    Bag of Words implementation of a Chat
    """
    
    def __init__(self,categories,fileVectors,fileVoc):
        Chat.__init__(self,categories,fileVectors)
        self.Vec=CountVectorizer(token_pattern='\\b[^ ]+\\b')
        self.fileVoc=fileVoc
        # Read the vocabulary from file
        self.Vec.vocabulary=self._readVoc(fileVoc)
        
    def multiClassLearner(self):
        """
        Defines the machine learning system to learn from vectors to categories
        Returns: Linear SVM for multi class
        """
        return RobustLinearSVC(C=0.01,random_state=1,dual='auto')
    
    def vectorize(self,normSen):
        """
        Transforms the normalized sentence in a vector object
        Params:
            normSen: string, normalized sentence
        Returns : [vector,entities]
            - vector   : vectorial representation of the normSem
            - entities : list of entities in the same order than in normSen
        """
        # Get the tokens and entities of the sentence
        
        # Get all tokens and entitites
        allTokens=self.Vec.build_tokenizer()(normSen)
        
        entities=[]
        tokens  =[]
        for tok in allTokens:
            if self.isEntity(tok):
                entities.append(tok)
            else:
                tokens.append(tok)

        # Insert the new tokens in the current vocabulary
        currVoc=self.Vec.vocabulary
        if type(currVoc)==type(None):
            currVoc={} # Empty dictionary
        newTok=False
        for tok in tokens:
            if tok not in currVoc:
                newTok=True
                currVoc[tok]=len(currVoc)
                print('Insert into vocabulary token "{}" with value {}'.format(tok,currVoc[tok]))
        if newTok:
            self.Vec=CountVectorizer(token_pattern='\\b[^ ]+\\b')
            self.Vec.vocabulary=currVoc
            self._writeVoc(currVoc,self.fileVoc)
            
        # Describe the sentence using all tokens
        vector=self.Vec.transform([normSen])[0].toarray()[0]
        print(normSen,'->',vector)
        return [vector,entities]
    
    def vectorToStr(self,vector):
        """
        Creates a string from vector suitable to store in a file and to get the
        original vector object from this string
        Returns : string
        """
        Str=''
        for v in vector:
            Str=Str+' {}'.format(v)
        return Str
    
    def vectorFromStr(self,vectorStr):
        """
        Creates a vector object from the string vectorStr. This string is generated
        using vectorToStr.
        Returns : vector object
        """
        return [float(v) for v in vectorStr.split(' ') if len(v)>0]
    
    def _writeVoc(self,voc,fileVoc):
        with open(fileVoc,'wt') as F:
            for v in voc:
                F.write('{} {}\n'.format(v,voc[v]))
    
    def _readVoc(self,fileVoc):
        voc={}
        try:
            with open(fileVoc,'rt') as F:
                print('Rading vocabulary from {}'.format(fileVoc))
                line=F.readline()
                while len(line)>0:
                    row=line.split('\n')[0]
                    row=row.split(' ')
                    tok=row[0]
                    v  =int(row[1])
                    voc[tok]=v
                    print('  Token "{}" as {}'.format(tok,voc[tok]))
                    
                    line=F.readline()
            return voc
                    
        except:
            return {} # Empty vocabulary

    # **************************************************
    # Designed for possible implementation in a child class

    def isEntity(self,tok):
        """
        If returns True this token will be cosiered a entity not, a token
        """
        return False


