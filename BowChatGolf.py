#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pocket Golf Agent
"""

import re
import math
from BoWChat import BoWChat

class BowChatGolf(BoWChat):
    """
    Chat interactivo para gestionar un juego de Golf mediante NLP
    """
    def __init__(self, fileVectors, fileVoc):
        # Tus 4 operadores definidos en la propuesta como categorías del clasificador
        self.categorias_golf = ['configurar_hoyo', 'elegir_palo', 'ejecutar_golpe', 'consultar_estado','reiniciar_juego', 'Ninguna']
        
        # Inicializamos la clase padre BoWChat con nuestras categorías de golf
        BoWChat.__init__(self, self.categorias_golf, fileVectors, fileVoc)
        
        # Estructura de datos para almacenar el Estado del Juego / STM
        self.estado = {
            "palo_actual": None,
            "distancia_restante": None,
            "hoyo_configurado": False
        }
        
        # STM para recordar el último golpe ejecutado (para la regla de repetición)
        self.ultima_potencia_golpe = None
    
    def normalizar_entidad(self, texto):
        """
        Mapea abreviaciones comunes a los términos oficiales del juego.
        """
        txt = texto.lower().strip()
        
        # Mapeo para tipos de palo
        if txt.startswith('cor') or txt in ['corto', 'corta', 'cortito', 'pequeño']: return 'corto'
        if txt.startswith('me') or txt in ['medio', 'media', 'medi']:     return 'medio'
        if txt.startswith('lar') or txt in ['largo', 'larga', 'larg', 'grande']:    return 'largo'
        
        # Mapeo para potencias (¡Aquí solucionamos tu problema!)
        if txt.startswith('baj') or txt in ['bajo', 'baja', 'ba', 'suave']:
            return 'bajo'
        if txt.startswith('alt') or txt in ['alto', 'alta', 'al', 'fuerte']:
            return 'alto'
        
        return txt

    def isEntity(self, tok):
        """
        Identifica si un token es una entidad (un argumento para nuestros operadores).
        En nuestro golf, las entidades son:
        - Números (ej: 150, 200, 50) que representan distancias.
        - Tipos de palo: 'corto', 'medio', 'largo'.
        - Potencias de golpe simuladas por texto: 'bajo', 'alto'.
        """
        tok_lower = tok.lower()
        # Es un número entero?
        if re.match(r'^\d+', tok_lower):
            return True
        # Lista de palabras válidas incluyendo las nuevas abreviaciones
        raices_validas = ['cor', 'med', 'me', 'lar', 'baj', 'alt']
        if any(tok_lower.startswith(raiz) for raiz in raices_validas):
            return True
            
        # Palabras completas por si acaso
        validas_extra = ['corto', 'corta', 'medio', 'media', 'largo', 'larga', 'bajo', 'baja', 'alto', 'alta']
        if tok_lower in validas_extra:
            return True
        return False
  
    def initialization(self):
        """
        Mensaje de bienvenida interactivo al estilo de una interfaz abierta.
        """
        print('='*60)
        print('⛳ ¡BIENVENIDO A POCKET GOLF AGENT! ⛳')
        print('='*60)
        print('La interfaz está abierta. Puedes proponer la acción que desees.')
        print('Sugerencias de lo que puedes hacer en lenguaje natural:')
        print('  • "Quiero configurar un hoyo de 150 metros"')
        print('  • "Voy a elegir el palo largo" o "palo medio" o "palo corto"')
        print('  • "Ejecutar golpe alto" o "golpe medio" o "potencia baja"')
        print('  • "Quiero consultar el estado actual" o "¿Cuánto falta?"')
        print('  • "Repite el último golpe" o "haz lo mismo que antes"')
        print('Escribe "Exit o Salir" para cerrar la aplicación.')
        print('='*60)
    
    def evalConfirm(self, model, vector):
        """
        INTERCEPTOR DE PREDICCIÓN: Forzamos la categoría usando heurística lingüística
        si el modelo estadístico aún no tiene suficientes datos entrenados.
        """
        # Obtenemos la frase normalizada que introdujo el usuario de forma indirecta
        # reconstruyendo los tokens activos en el vector actual.
        tokens_activos = [tok for tok, idx in self.Vec.vocabulary_.items() if vector[idx] > 0]
        frase = " ".join(tokens_activos).lower()
        contiene_numero = any(tok.isdigit() for tok in self.Vec.vocabulary_)

        # Si el usuario metió un número (ej: "120") o palabras afines, va directo a configurar hoyo (Categoría 0)
        if contiene_numero or "configurar" in frase or "hoyo" in frase or "distancia" in frase:
            prediccion_forzada = 0 # 'configurar_hoyo'
            self.presentCategory(prediccion_forzada)
            return self.askForRealCategory(prediccion_forzada)

        # Regla 1: Si contiene números o palabras de configuración, es configurar_hoyo
        if any(tok.isdigit() for tok in tokens_activos) or "configurar" in frase or "hoyo" in frase or "distancia" in frase:
            prediccion_forzada = 0 # 'configurar_hoyo'
            self.presentCategory(prediccion_forzada)
            return self.askForRealCategory(prediccion_forzada)

        # Regla 2: Si habla de golpear, tirar o potencias, es ejecutar_golpe
        if "golpe" in frase or "potencia" in frase or "ejecutar" in frase or "tirar" in frase or "pegar" in frase or "golpear" in frase:
            prediccion_forzada = 2 # 'ejecutar_golpe'
            self.presentCategory(prediccion_forzada)
            return self.askForRealCategory(prediccion_forzada)

        # Regla 3: Si habla de elegir o menciona tipos de palo, es elegir_palo
        if "palo" in frase or "seleccionar" in frase or "elegir" in frase:
            prediccion_forzada = 1 # 'elegir_palo'
            self.presentCategory(prediccion_forzada)
            return self.askForRealCategory(prediccion_forzada)

        # Regla 4: Si pregunta por ver, estado, consultar o cuánto falta
        if "consultar" in frase or "estado" in frase or "ver" in frase or "score" in frase:
            prediccion_forzada = 3 # 'consultar_estado'
            self.presentCategory(prediccion_forzada)
            return self.askForRealCategory(prediccion_forzada)
        
        # Regla 5: Si habla de reiniciar o resetear el juego
        if "reiniciar" in frase or "resetear" in frase or "nuevo" in frase:
            prediccion_forzada = 4 # 'reiniciar_juego'
            self.presentCategory(prediccion_forzada)
            return self.askForRealCategory(prediccion_forzada)

        # Si no cumple ninguna regla obvia, dejamos que el modelo original decida
        return BoWChat.evalConfirm(self, model, vector)

    def STMEntities(self, entities, catIndex, prevResult):
        """
        Implementación de Reglas de Memoria a Corto Plazo (STM)
        """
        categoria = self.categories[catIndex]
        if categoria == 'Ninguna':
            return entities  # No aplicamos STM si no se detectó ninguna categoría válida
        
        # REGLA STM 0: configurar_hoyo interactivo (Pide el dato si falta)
    
        if categoria == 'configurar_hoyo' and len(entities) == 0:
            print("🤖 Queve-Caddy: Quieres configurar un hoyo, pero no indicaste los metros en la frase.")
            print("👉 ¿A qué distancia se encuentra el hoyo? (Ejemplo: 150)")
            distancia_ingresada = input("Distancia > ").strip()
            
            # Buscamos si introdujo números en su respuesta por teclado
            match = re.search(r'\d+', distancia_ingresada)
            if match:
                entities.append(match.group())
            else:
                print("ℹ️ STM: Entrada no válida. Inicializando a 100 metros por defecto por seguridad.")
                entities.append('100')

        # REGLA STM 1: Si el usuario quiere 'elegir_palo' pero no especificó el tipo de palo, le preguntamos directamente y usamos su respuesta.
        if categoria == 'elegir_palo' and len(entities) == 0:
            # Le preguntamos abiertamente al usuario
            print("🤖 Queve-Caddy: No has especificado el tipo de palo en la frase.")
            if self.estado["palo_actual"]:
                print(f"   (Palo actual en uso: '{self.estado['palo_actual'].upper()}')")
                
            print("👉 ¿Cuál prefieres? Escribe: corto, medio o largo")
            palo_elegido = input("Palo > ").strip().lower()
            palo_normalizado = self.normalizar_entidad(palo_elegido)

            if palo_normalizado in ['corto', 'medio', 'largo']:
                entities.append(palo_normalizado)
            else:
                # Si el usuario pulsa Enter o escribe cualquier otra cosa, recién ahí aplicamos el histórico por seguridad
                if self.estado["palo_actual"]:
                    print(f"ℹ️ STM: Opción no válida. Manteniendo último usado: '{self.estado['palo_actual']}'")
                    entities.append(self.estado["palo_actual"])
                else:
                    print("ℹ️ STM: No hay palo previo. Usando 'medio' por defecto.")
                    entities.append('medio')
        
        # REGLA STM 2: Si quiere 'ejecutar_golpe' pero olvidó la potencia, usamos una media por defecto
        # o recuperamos el histórico si existe.
        if categoria == 'ejecutar_golpe' and len(entities) == 0:
            print("🤖 Queve-Caddy: Vas a ejecutar un golpe, pero no indicaste la potencia.")
            print("👉 ¿Con qué potencia deseas golpear? Escribe: bajo, medio o alto")
            
            # Si el usuario tiene un histórico de golpes, se lo sugerimos de forma interactiva
            if self.ultima_potencia_golpe:
                print(f"   (Pulsa ENTER para repetir tu último golpe: '{self.ultima_potencia_golpe.upper()}')")
                
            potencia_elegida = input("Potencia > ").strip().lower()
            potencia_normalizada = self.normalizar_entidad(potencia_elegida)

            if potencia_normalizada in ['bajo', 'medio', 'alto']:
                entities.append(potencia_normalizada)
            elif len(potencia_elegida) == 0 and self.ultima_potencia_golpe:
                # Si el usuario da ENTER vacío, la STM recupera el golpe previo de forma inteligente
                print(f"ℹ️ STM: Recordando y repitiendo potencia previa: '{self.ultima_potencia_golpe}'")
                entities.append(self.ultima_potencia_golpe)
            else:
                print("ℹ️ STM: Opción no válida. Usando potencia 'medio' por defecto.")
                entities.append('medio')
        # REGLA STM 3: Si quiere 'reiniciar_juego' pero no envió el parámetro de confirmación en la frase
        if categoria == 'reiniciar_juego' and len(entities) == 0:
            print("⚠️ Caddy: ¿Estás seguro de que quieres borrar tu progreso actual y reiniciar?")
            conf = input("Responde (si/no): ").strip().lower()
            if conf in ['si', 'sí', 'confirmar', 'yes']:
                entities.append('si')
                    
                self.estado = {
                    "palo_actual": None,
                    "distancia_restante": None,
                    "hoyo_configurado": False
                }
                self.ultima_potencia_golpe = None
            else:
                entities.append('no')
        return entities

    def agent(self, catIndex, entities):
        """
        Lógica del Agente: Ejecuta los 4 operadores basándose en la categoría
        detectada y las entidades extraídas/recuperadas por STM.
        """
        categoria = self.categories[catIndex]
        if categoria == 'Ninguna':
            print("\n🔄 [Acción Cancelada] Volviendo a la interfaz inicial. ¿Qué más deseas hacer?")
            return None # Retorna limpio y el bucle principal de Chat.py vuelve a pedir un input

        print(f"\n🤖 Queve-Caddy: Ejecutando operador: {categoria} | Datos: {entities}")
        

        # -------------------------------------------------------------
        # OPERADOR 1: configurar_hoyo(distancia)
        # -------------------------------------------------------------
        if categoria == 'configurar_hoyo':
            distancia = None
            
            # Buscamos un número dentro de la lista de entidades
            for ent in entities:
                match = re.search(r'\d+', str(ent))
                if match:
                    distancia = int(match.group())
                    break
            
            # Si no estaba en entities, buscamos en el vocabulario activo por si acaso
            if distancia is None:
                for tok in self.Vec.vocabulary_:
                    match = re.search(r'\d+', str(tok))
                    if match:
                        distancia = int(match.group())
                        break

            # Si encontramos el número, guardamos el estado con éxito
            if distancia is not None:
                self.estado["distancia_restante"] = distancia
                self.estado["hoyo_configurado"] = True  
                print(f"⛳ Hoyo inicializado a {distancia} metros del objetivo.")
            else:
                print("🤖 Queve-Caddy: Necesito que indiques una distancia numérica para configurar el hoyo.")
                
            return self.estado["distancia_restante"]

        # -------------------------------------------------------------
        # OPERADOR 2: elegir_palo()
        # -------------------------------------------------------------
        if categoria == 'elegir_palo':
            palo = None
            for ent in entities:
                ent_norm = self.normalizar_entidad(ent)
                if ent_norm in ['corto', 'medio', 'largo']:
                    palo = ent_norm
                    break
            
            if palo:
                self.estado["palo_actual"] = palo
                print(f"🏌️ Palo seleccionado con éxito: '{palo.upper()}'")
            else:
                print("🤖 Queve-Caddy: No detecté un tipo de palo válido (corto, medio, largo).")
            return self.estado["palo_actual"]

        # -------------------------------------------------------------
        # OPERADOR 3: ejecutar_golpe(potencia_texto)
        # -------------------------------------------------------------
        if categoria == 'ejecutar_golpe':
            # REGLA A: Validar si el hoyo ha sido configurado
            if not self.estado["hoyo_configurado"] or self.estado["distancia_restante"] is None:
                print("⚠️ 🤖 Queve-Caddy: ¡No puedes golpear! El hoyo no ha sido configurado todavía.")
                print("👉 Por favor, primero escribe algo como 'configurar hoyo a 150 metros'.")
                return None

            # Validar PRIMERO si hay un palo seleccionado en esta partida
            if self.estado["palo_actual"] is None:
                print("⚠️ 🤖 Queve-Caddy: ¡No puedes golpear la bola! No has elegido ningún palo para esta partida todavía.")
                print("👉 Por favor, escribe algo como 'elegir palo medio' o 'quiero el palo corto' antes de tirar.")
                return None
            
            # Si hay palo, extraemos la potencia de las entidades
            potencia = 'medio' 
            for ent in entities:
                ent_norm = self.normalizar_entidad(ent)
                if ent_norm in ['bajo', 'medio', 'alto']:
                    potencia = ent_norm
                    break
            
            self.ultima_potencia_golpe = potencia
            
            matriz_distancias = {
                'largo': {'bajo': 40,  'medio': 70,  'alto': 100},
                'medio': {'bajo': 20,  'medio': 45,  'alto': 65},
                'corto': {'bajo': 5,   'medio': 15,  'alto': 25}
            }
            
            palo_act = self.estado["palo_actual"]
            metros_recorridos = matriz_distancias[palo_act][potencia]
            
            if self.estado["distancia_restante"] >= 0:
                # Si es positivo, el hoyo está adelante: avanzamos restando distancia
                self.estado["distancia_restante"] -= metros_recorridos
            else:
                # Si es negativo, el hoyo quedó atrás: nos devolvemos sumando metros hacia el cero
                self.estado["distancia_restante"] += metros_recorridos
            
            print(f"¡ZAS! 🏑 Golpe con palo '{palo_act.upper()}' y 💥 potencia '{potencia.upper()}'.")
            print(f"🪩 La bola avanzó {metros_recorridos} metros.")
            
            dist_absoluta = abs(self.estado["distancia_restante"])
            
            if dist_absoluta <= 2.5:
                print(f"\n🎉🥳 ¡ENHORABUENA! La bola quedó a {dist_absoluta:.1f} metros del objetivo.")
                print("⛳¡La bola ha entrado en el hoyo! Juego terminado. 🥳🎉")
                self.estado["hoyo_configurado"] = False
                self.estado["distancia_restante"] = 0 # Reseteamos a cero exacto por limpieza
            else:
                # Si no ha entrado, evaluamos el estado para dar el mensaje correcto al jugador
                if self.estado["distancia_restante"] < 0:
                    # El valor es negativo: Por haberse pasado
                    print(f"🛑 ¡Te has pasado! El hoyo quedó atrás. Te falta para devolverte {dist_absoluta:.1f} metros.")
                else:
                    # El valor sigue siendo positivo: se quedó corto
                    print(f"🎯 Aun te falta. Distancia restante al hoyo: {self.estado['distancia_restante']:.1f} metros.")
                
            return self.estado["distancia_restante"]

        # -------------------------------------------------------------
        # OPERADOR 4: consultar_estado()
        # -------------------------------------------------------------
        if categoria == 'consultar_estado':
            print(f"📊 [ESTADO DEL JUEGO]")
            print(f"   • Distancia restante: {self.estado['distancia_restante']} metros.")
            print(f"   • Palo en mano: {self.estado['palo_actual'] if self.estado['palo_actual'] else 'Ninguno'}")
            return self.estado["distancia_restante"]

        # -------------------------------------------------------------
        # OPERADOR 5: reiniciar_juego()
        # -------------------------------------------------------------
        if categoria == 'reiniciar_juego':
            confirmacion = 'no'
            for ent in entities:
                if ent.lower() in ['si', 'no']:
                    confirmacion = ent.lower()
                    break
                    
            if confirmacion == 'si':
                # El estado ya fue limpiado con éxito en STMEntities
                print("\n🔄 [Juego Reiniciado] Se ha borrado todo el progreso y registros del caddy.")
                print("🤖 Queve-Caddy: Empezamos de nuevo, quiza podríar iniciar configurando la distancia al hoyo .")
            else:
                print("\n [Reinicio Cancelado] Continuamos en la partida actual sin cambios.")
            return self.estado["hoyo_configurado"]

#%% Bucle de ejecución del programa
if __name__ == "__main__":
    # Nombres de los archivos donde el sistema guardará su aprendizaje y su vocabulario interactivo
    fileVec = 'GolfAgente.vec'
    fileVoc = 'GolfAgente.voc'
    
    # Instanciamos y corremos el juego
    JuegoGolf = BowChatGolf(fileVec, fileVoc)
    JuegoGolf.run()