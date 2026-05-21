#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author quevedo@uniovi.es 
"""
import numpy as np

class Chat:
    """
    Abstract class that implements a generic chat
    """

    def __init__(self,categories,fileVectors):
        """
        Params:
            - categories  : Array of strings with the categories' names
            - fileVectors : Path to a file storing sentence vectors, representing 
                             transformed sentences along with their category labels.
        """
        self.categories =categories
        self.fileVectors=fileVectors
    
    def run(self):
        """
        Starts a dialog. 
        Each sentence will be transformed in a vector.
        The user will indicate the category.
        Category and vector will be appened to self.fileVectors
        """
        self._createFileVectors()
        self.initialization()
        Exit=False
        result=None
        while(not Exit):
            model   =self.getModelFromFile()  # Reads the vectors from self.fileVectors and learn the model
            sentence=self.prompt()            # User's prompt
            if self.isExit(sentence):         # Exit condition
                print("\n🏌️ Gracias por jugar Pocket Golf Agent")
                print("👋 Vuelve pronto")
                Exit=True
                continue
            normSen =self.normalize(sentence)                   # Normalizes the sentence
            [vector,entities]  =self.vectorize(normSen)         # Transforms to a vector the normalized sentence
            catIndex=self.evalConfirm(model,vector)             # Evals vector and to ask the user for the correct category
            entities=self.STMEntities(entities,catIndex,result) # Use Short Term Memmory to define the entities
            self.updateFileVectors(catIndex,vector)             # Inserts a new example in the fileVectors
            result=self.agent(catIndex,entities)                # Call to the agent using the category(action) and entities (data)
            
    def getModelFromFile(self):
        """
        Create a multiclass model from the examples in self.fileVectors
        """
        # Create the dataset
        X=[]
        Y=[]
        with open(self.fileVectors,'rt') as F:
            line=F.readline()
            while len(line)>0:
                line=line.split('\n')[0]
                [cat,vectorStr]=line.split('|')
                catInd=int(cat)
                # vector=self.vectorFromStr(vectorStr)
                # X.append(self.vectorToArray(vector))
                X.append(self.vectorFromStr(vectorStr))
                Y.append(catInd)
                
                line=F.readline()
        
        # Create the model
        model=self.multiClassLearner()
        model.fit(X,Y)
        return model

    def evalConfirm(self,model,vector):
        PreCat=model.predict([vector])[0]
        self.presentCategory(PreCat)
        RealCat=self.askForRealCategory(PreCat)
        return RealCat
    
    def updateFileVectors(self,catIndex,vector):
        """
        Appends the example y=catIndex, x=vector to the vectors' file
        """
        with open(self.fileVectors,'at') as F: 
            F.write('{}|'.format(catIndex))
            F.write('{}\n'.format(self.vectorToStr(vector)))
    
    def _createFileVectors(self):
        try:
            with open(self.fileVectors,'rt') as F:
                pass
        except:
            # If not exists
            open(self.fileVectors,'wt')
            print('File "{}" not exists. Created'.format(self.fileVectors))
    
    
    # **************************************************
    # Designed for possible implementation in a child class

    def initialization(self):
        """
        Previous actions before chat loop.
        Welcome to users
        """
        print('Welcome to chat.\nType "exit" to quit from the chat.')
        
    def prompt(self):
        """
        Prompt: Enter a sentence.
        Returns: string with the sentence
        """
        sentence=input("> ")
        return sentence
        
    def isExit(self,sentence):
        """
        Exit criterium
        Returns True if sentence is an exit instruction
        """
        sentence = sentence.lower().strip()

        return sentence in [
            'exit',
            'salir',
            'terminar',
            'cerrar juego',
            'fin',
            'quit'
        ]
    
    def normalize(self,sentence):
        """
        Normalization process. 
        Params:
            - sentence : string with a sentence
        Returns: a string with a normalizated sentence.
                 The current implementation does no modify the sentence
        """
        return sentence    
    
    def presentCategory(self, PreCat):
        """
        Informa al usuario cuál es la categoría predicha en español
        """
        print('Categoría detectada: {}'.format(self.categories[PreCat]), end='')
        
    def askForRealCategory(self, PreCat):
        # 1. Mensaje de confirmación inicial totalmente en español
        print('. ¿Es esto correcto? (Sí/Yes [default], No)? ', end='')
        YesNo = input().strip().lower()
        
        # Si el usuario pulsa ENTER sin escribir nada, se acepta el valor por defecto (SÍ)
        if len(YesNo) == 0: 
            return PreCat
            
        # Variaciones de aceptación en español e inglés
        afirmaciones = ['si', 'sí', 'yes', 's', 'y', 'ok', 'correcto']
        negaciones = ['no', 'n', 'incorrecto']
        
        if YesNo in afirmaciones or (YesNo[0] in ['s', 'y', 'o'] and YesNo not in negaciones):
            return PreCat
            
        # 2. Si dice que NO, mostramos el menú interactivo en español
        inputOK = False
        while not inputOK:
            print("\n--- Categorías Disponibles ---")
            for icat in range(len(self.categories)):
                print('{} : {}'.format(icat, self.categories[icat]))
            
            print('Ingrese el número de la categoría correcta:')
            indCat = input().strip()
            
            if indCat.isnumeric():
                RealCat = int(indCat)
                inputOK = RealCat >= 0 and RealCat < len(self.categories)
                
            if not inputOK:
                print('❌ Respuesta incorrecta. Por favor, introduce un índice de categoría válido.')
                
        return RealCat
            
    def agent(self,catIndex,entities):
        """
        Implements the action catIndex, using the data in entities
        Returns: result , generic result information
        """
        print('Agent: Action:{} Data:'.format(self.categories[catIndex]),end='')
        for ent in entities:
            print(' {}'.format(ent),end='')
        print()
        return '({} {})'.format(self.categories[catIndex],entities)
        
        
    def STMEntities(self,entities,catIndex,prevResult):
        """
        Define the entities using Short Term Memory
        Params:
            entities  : list of entities in the same order than are placed in the sentence
            catIndex  : integer, index of the category
            prevResult: the return value of the agent in the last interaction
        Returns:
            entities : list of entities 
        """
        return entities
    
    # **************************************************
    # Must be implemented in the child class    
    
    def multiClassLearner(self):
        """
        Defines the machine learning system to learn from vectors to categories
        Returns: a sklearn (or compatible) object that can handle multiclass learning
        """
        pass
    
    def vectorize(self,normSen):
        """
        Transforms the normalized sentence in a vector object
        Params:
            normSen: string, normalized sentence
        Returns : [vector,entities]
            - vector   : vectorial epresentation of the normSem
            - entities : list of entities in the same order than in normSen
        """
        pass
    
    def vectorToStr(self,vector):
        """
        Creates a string from vector suitable to store in a file and to get the
        original vector object from this string
        Returns : string
        """
        pass
    
    def vectorFromStr(self,vectorStr):
        """
        Creates a vector object from the string vectorStr. This string is generated
        using vectorToStr.
        Returns : vector object
        """
        pass
    

    




        
        