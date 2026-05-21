#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: quevedo@uniovi.es
"""

""" 
EJERCICIO 1  :  Calculadora agente
A) Crea      : BowChatCalculadora_E1_Agente como hija de BowChatCalculadora
B) Implementa: en agent (ver Chat) la operación.
                NOTA: self.categories[catIndex] es la cadena del operador
                NOTA: Crear la cadena con la operación a partir del operador y
                        las dos entities. Utilizar eval para evaluarla y obtener 
                        un valor numérico. Retorna este valor.
C) Prueba    : el agente de este chat 
"""


from BowChatCalculadora import BowChatCalculadora


class BowChatCalculadora_E1_Agente(BowChatCalculadora):
    
    def agent(self,catIndex,entities):
        """
        Implements the operation
        Returns: the numeric value of the operation
        """
        operacion='{}{}{}'.format(entities[0],self.categories[catIndex],entities[1])
        resultado=eval(operacion)
        print('Agente: {}={}'.format(operacion,resultado))
        return resultado

"""
EXTENSIÓN : Haz que cuando el usuario escriba pi este se considere como una entidad
              cuyo valor desde el punto de vista del agente sea math.pi
A) Crea   : BowChatCalculadora_E1b_AgentePI como hija de BowChatCalculadora_E1_Agente
PISTA     : Modifica BowChatCalculadora.isEntity para que admita pi como entidad
PISTA     : Crea un agente que cambie pi por str(math.pi).
            Luego llama al agente de la clase padre 
"""

import math
import re
class BowChatCalculadora_E1b_AgentePI(BowChatCalculadora_E1_Agente):
    def isEntity(self,tok):
        """
        If returns True this token will be cosiered a entity not, a token
        """
        # return type(re.fullmatch(r'[-+]?\d+',tok))!=type(None)
        return type(re.fullmatch(r'pi|[-+]?\d+',tok))!=type(None)

        # La línea comentada es el código de la clase BowChatCalculadora
        # Fíjate que el único cambio es 'pi|' que indica que además de la secuencia
        #   de dígitos se admite la cadena pi
        
    def agent(self,catIndex,entities):
        # Convertir pi en math.pi
        if entities[0]=='pi':
            entities[0]=str(math.pi)
        if entities[1]=='pi':
            entities[1]=str(math.pi)
            
        # Programación alternativa vectorial
        # entities=[str(math.pi) if ent=='pi' else ent for ent in entities]
            
        # Llamar al agente de la clase padre
        return BowChatCalculadora_E1_Agente.agent(self,catIndex,entities)

#%% Ejemplo de uso
if __name__ == "__main__":
    fileVec='CalculadoraAge.vec'
    fileVoc='CalculadoraAge.voc'
    # Calculadora=BowChatCalculadora_E1_Agente(fileVec,fileVoc)    # Con agente que realiza la operación
    Calculadora=BowChatCalculadora_E1b_AgentePI(fileVec,fileVoc) # Extensión
    Calculadora.run()

