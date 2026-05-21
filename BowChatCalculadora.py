#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: quevedo@uniovi.es
"""

from BoWChat import BoWChat
import re

class BowChatCalculadora(BoWChat):
    """
    Crea un chat de una calculadora donde las operaciones son: '+','-','*','/'
      y los operandos son enteros
    """
    def __init__(self,fileVectors,fileVoc):
        categories   =['+','-','*','/']
        BoWChat.__init__(self,categories,fileVectors,fileVoc)
        
    def isEntity(self,tok):
        """
        If returns True this token will be cosiered a entity not, a token
        """
        return type(re.fullmatch(r'[-+]?\d+',tok))!=type(None)


#%% Ejemplo de uso
if __name__ == "__main__":
    fileVec='Calculadora.vec'
    fileVoc='Calculadora.voc'
    Calculadora=BowChatCalculadora(fileVec,fileVoc)
    Calculadora.run()

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
"""
EXTENSIÓN : Haz que cuando el usuario escriba pi este se considere como una entidad
              cuyo valor desde el punto de vista del agente sea math.pi
A) Crea   : BowChatCalculadora_E1b_AgentePI como hija de BowChatCalculadora_E1_Agente
PISTA     : Modifica BowChatCalculadora.isEntity para que admita pi como entidad
PISTA     : Crea un agente que cambie pi por str(math.pi).
            Luego llama al agente de la clase padre 
"""


""" 
EJERCICIO 2  :  Calculadora con Short Term Memory
A) Piensa    : reglas STM para cuando falten entities(operandos) en la calculadora
B) Crea      : BowChatCalculadora_E2_STM como hija de BowChatCalculadora_E1_Agente
C) Crea      : las estructuras de datos (ED) para almacenar STM
D) Implementa: en STMEntities (ver Chat) las reglas STM usando las ED de C)
E) Prueba    : la STM de este chat 
"""

""" 
EJERCICIO 3  :  Calculadora con Información Extra: Emociones
A) Piensa    : Diferentes emociones (solo la palabra)
B) Crea      : BowChatCalculadora_E3_ExtraInfo como hija de BowChatCalculadora_E2_STM
C) Pregunta  : por las emocinones
D) Implementa: añade la codificación de las emociones al vector que describe la frase
E) Prueba    : el uso de las emociones
"""


